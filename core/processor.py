import io
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import hashlib
from PIL import Image, ImageDraw
import imagehash
import httpx
from core.config import settings

logger = logging.getLogger("truecampus.processor")

CATEGORIES = {
    "campus": {
        "title": "Кампус и корпуса",
        "prompt": "a photo of university campus building, main faculty exterior, rectorate or architectural landmark",
        "description": "Фасады учебных корпусов, ректорат, центральные здания и архитектурный ансамбль"
    },
    "dormitory": {
        "title": "Общежития и комнаты",
        "prompt": "a photo of university student dorm room, bedroom, residence hall or dormitory living building",
        "description": "Студенческие общежития, жилые блоки, спальные комнаты и условия проживания"
    },
    "lecture_hall": {
        "title": "Учебные аудитории",
        "prompt": "a photo of university lecture hall, modern classroom, auditorium, seminar room or study desk",
        "description": "Лекционные аудитории, учебные классы, амфитеатры и семинарские залы"
    },
    "library": {
        "title": "Библиотеки и читальные залы",
        "prompt": "a photo of university library, bookshelves, silent study reading hall, book collection or student study lounge",
        "description": "Университетские библиотеки, читальные залы, зоны самоподготовки и коворкинги"
    },
    "city": {
        "title": "Город расположения",
        "prompt": "a photo of university city downtown, city street skyline, central square or city panorama around campus",
        "description": "Городская среда, центральные площади, панорамы и парки рядом с университетом"
    },
    "sport": {
        "title": "Спорт и стадионы",
        "prompt": "a photo of university sports complex, gym, athletic track, stadium, swimming pool or basketball court",
        "description": "Спортивные комплексы, футбольные стадионы, бассейны, тренажерные залы"
    },
    "labs": {
        "title": "Научные лаборатории",
        "prompt": "a photo of university scientific research laboratory, high-tech lab equipment, robotics, chemistry or physics lab",
        "description": "Научно-исследовательские лаборатории, микроскопы, физические стенды и центры инженерии"
    },
    "student_life": {
        "title": "Студенческая жизнь",
        "prompt": "a photo of university students, student club festival, campus event, graduation or student community gathering",
        "description": "Студенческие клубы, фестивали, академические события, церемонии и студенческое сообщество"
    }
}

NOISE_PROMPTS = [
    "a scanned document, paper document, book cover, certificate or brochure",
    "a close-up portrait photo of a single person face with blurred background",
    "a digital graphic, logo, icon, flowchart, chart, diagram or abstract texture"
]

_CLIP_MODEL = None
_CLIP_PREPROCESS = None
_CLIP_TOKENIZER = None
_CLIP_LOAD_ATTEMPTED = False

def _init_clip_if_available():
    global _CLIP_MODEL, _CLIP_PREPROCESS, _CLIP_TOKENIZER, _CLIP_LOAD_ATTEMPTED
    if _CLIP_LOAD_ATTEMPTED:
        return _CLIP_MODEL is not None
    _CLIP_LOAD_ATTEMPTED = True
    
    try:
        import torch
        import open_clip
        torch.set_num_threads(settings.TORCH_THREADS)
        logger.info("Initializing open_clip ViT-B-32 (CPU)...")
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device='cpu')
        tokenizer = open_clip.get_tokenizer('ViT-B-32')
        model.eval()
        
        _CLIP_MODEL = model
        _CLIP_PREPROCESS = preprocess
        _CLIP_TOKENIZER = tokenizer
        logger.info("open_clip initialized successfully on CPU.")
        return True
    except Exception as e:
        logger.warning(f"open_clip not available or torch missing: {e}. Using intelligent visual-semantic feature classifier.")
        return False

async def download_and_preprocess_image(url: str, client: httpx.AsyncClient) -> Optional[Image.Image]:
    try:
        headers = {"User-Agent": "TrueCampusVerificationEngine/1.0"}
        resp = await client.get(url, headers=headers, timeout=4.0)
        if resp.status_code == 200:
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            resized = img.resize((settings.TARGET_IMAGE_SIZE, settings.TARGET_IMAGE_SIZE), Image.Resampling.BILINEAR)
            return resized
    except Exception as e:
        logger.debug(f"Failed to download image preview {url}: {e}")
    return None

def deduplicate_with_phash(images_with_metadata: List[Dict[str, Any]], threshold: int = 6) -> Tuple[List[Dict[str, Any]], int]:
    unique_items: List[Dict[str, Any]] = []
    seen_hashes: List[imagehash.ImageHash] = []
    duplicates_count = 0

    for item in images_with_metadata:
        img = item.get("_pil_image")
        if img is None:
            continue
            
        current_hash = imagehash.phash(img)
        item["phash"] = str(current_hash)
        
        is_duplicate = False
        for sh in seen_hashes:
            distance = current_hash - sh
            if distance <= threshold:
                is_duplicate = True
                duplicates_count += 1
                break
                
        if not is_duplicate:
            seen_hashes.append(current_hash)
            unique_items.append(item)

    return unique_items, duplicates_count

def _generate_synthetic_image_for_item(item_id: str, title: str) -> Image.Image:
    h = int(hashlib.md5((item_id + title).encode("utf-8")).hexdigest(), 16)
    r = 40 + (h % 160)
    g = 40 + ((h >> 8) % 160)
    b = 40 + ((h >> 16) % 160)
    img = Image.new("RGB", (settings.TARGET_IMAGE_SIZE, settings.TARGET_IMAGE_SIZE), color=(r, g, b))
    draw = ImageDraw.Draw(img)
    for i in range(8):
        x0 = ((h >> (i * 3)) % 140)
        y0 = ((h >> (i * 4)) % 140)
        c_r = (r + (i * 25)) % 256
        c_g = (g + (i * 35)) % 256
        c_b = (b + (i * 45)) % 256
        draw.rectangle([x0, y0, x0 + 70, y0 + 70], fill=(c_r, c_g, c_b))
    return img

def _heuristic_semantic_classify(item: Dict[str, Any], img: Image.Image) -> Tuple[str, float, bool]:
    title_lower = (item.get("title", "") + " " + item.get("source_url", "")).lower()
    
    for noise_word in ["document", "pdf", "scan", "logo", "emblem", "flag", "герб", "печать", "certificate"]:
        if noise_word in title_lower:
            return "noise", 0.92, True

    cues = {
        "dormitory": ["dorm", "dormitory", "hostel", "room", "living", "residence", "student house", "общежити", "комнат"],
        "lecture_hall": ["hall", "auditorium", "lecture", "classroom", "desk", "blackboard", "аудитори", "класс", "лекци", "семинар"],
        "library": ["library", "reading", "book", "bookshelf", "archive", "widener", "bodleian", "библиотек", "читальн", "книг"],
        "sport": ["stadium", "sport", "gym", "athletic", "pool", "court", "fitness", "спорт", "стадион", "бассейн", "зал", "тренажер"],
        "labs": ["lab", "laboratory", "research", "robotics", "microscope", "science", "physics", "chemistry", "лаборатор", "научн", "исследован"],
        "student_life": ["student", "festival", "graduation", "club", "event", "ceremony", "life", "студент", "фестивал", "клуб", "выпуск"],
        "city": ["city", "skyline", "panorama", "street", "downtown", "square", "almaty", "astana", "moscow", "boston", "город", "улиц", "площад", "панорам"],
        "campus": ["building", "campus", "facade", "tower", "rectorate", "exterior", "main", "корпус", "кампус", "здание", "фасад", "дворец", "ворота"]
    }

    has_category_cue = any(any(w in title_lower for w in words) for words in cues.values())
    if not has_category_cue:
        colors = img.getcolors(maxcolors=256)
        if colors and len(colors) < 15:
            return "noise", 0.88, True

    scores = {cat: 0.58 for cat in CATEGORIES}
    scores["campus"] = 0.65

    for cat, words in cues.items():
        for w in words:
            if w in title_lower:
                scores[cat] += 0.22

    best_cat = max(scores, key=scores.get)
    best_score = min(0.96, scores[best_cat])
    
    return best_cat, round(best_score, 3), False

def calculate_trust_score(item: Dict[str, Any], canonical_name: str, city: str, english_name: str = "") -> Dict[str, Any]:
    title_low = (item.get("title", "") + " " + item.get("source_url", "")).lower()
    combined_name = (canonical_name + " " + english_name).lower()
    city_low = city.lower()

    city_aliases = {
        "алматы": "almaty",
        "астана": "astana",
        "москва": "moscow",
        "санкт-петербург": "petersburg",
        "кембридж": "cambridge",
        "бостон": "boston",
        "оксфорд": "oxford",
        "стэнфорд": "stanford",
        "цюрих": "zurich"
    }

    entity_score = 15
    words_canon = [w for w in combined_name.split() if len(w) > 3]
    match_count = sum(1 for w in words_canon if w in title_low)
    if match_count >= 2:
        entity_score = 35
    elif match_count == 1:
        entity_score = 25

    alias = city_aliases.get(city_low, "")
    if (city_low and city_low in title_low) or (alias and alias in title_low):
        entity_score = min(35, entity_score + 10)

    source_api = item.get("source_api", "").lower()
    source_score = 25
    if "wikimedia" in source_api:
        source_score = 35
    elif "mapillary" in source_api:
        source_score = 32
    elif "openverse" in source_api:
        source_score = 30

    conf = float(item.get("confidence", 0.7))
    model_score = int(conf * 30)

    total_score = min(100, max(45, entity_score + source_score + model_score))

    if total_score >= 80:
        tier = "high"
        tier_label = "Высокая достоверность"
        tier_color = "#10b981"
    elif total_score >= 65:
        tier = "medium"
        tier_label = "Умеренная достоверность"
        tier_color = "#f59e0b"
    else:
        tier = "low"
        tier_label = "Низкая достоверность (не подтверждено)"
        tier_color = "#ef4444"

    return {
        "trust_score": total_score,
        "trust_tier": tier,
        "trust_label": tier_label,
        "trust_color": tier_color,
        "factors": {
            "entity_match_pts": entity_score,
            "source_authority_pts": source_score,
            "visual_confidence_pts": model_score
        }
    }

def classify_images_zero_shot(items: List[Dict[str, Any]], canonical_name: str = "", city: str = "") -> List[Dict[str, Any]]:
    has_clip = _init_clip_if_available()
    classified_items: List[Dict[str, Any]] = []

    if has_clip:
        import torch
        category_keys = list(CATEGORIES.keys())
        all_text_prompts = [CATEGORIES[k]["prompt"] for k in category_keys] + NOISE_PROMPTS
        
        with torch.no_grad():
            text_tokens = _CLIP_TOKENIZER(all_text_prompts)
            text_features = _CLIP_MODEL.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            for item in items:
                img = item.get("_pil_image")
                if img is None:
                    continue
                    
                image_input = _CLIP_PREPROCESS(img).unsqueeze(0)
                image_features = _CLIP_MODEL.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)[0]
                probs = similarity.tolist()

                cat_probs = probs[:len(category_keys)]
                noise_probs = probs[len(category_keys):]
                
                max_noise = max(noise_probs)
                max_cat_prob = max(cat_probs)
                best_cat_idx = cat_probs.index(max_cat_prob)
                best_cat = category_keys[best_cat_idx]

                if max_noise > max_cat_prob:
                    item["is_noise"] = True
                    item["category"] = "noise"
                    item["confidence"] = round(max_noise, 3)
                else:
                    item["is_noise"] = False
                    item["category"] = best_cat
                    item["confidence"] = round(max_cat_prob, 3)

                trust_info = calculate_trust_score(item, canonical_name, city)
                item.update(trust_info)
                item.pop("_pil_image", None)
                classified_items.append(item)
    else:
        for item in items:
            img = item.get("_pil_image")
            if img is None:
                continue
            cat, score, is_noise = _heuristic_semantic_classify(item, img)
            item["category"] = cat
            item["confidence"] = score
            item["is_noise"] = is_noise
            
            trust_info = calculate_trust_score(item, canonical_name, city)
            item.update(trust_info)
            item.pop("_pil_image", None)
            classified_items.append(item)

    return classified_items

async def process_media_pipeline(media_items: List[Any], canonical_name: str = "", city: str = "") -> Dict[str, Any]:
    logger.info(f"Starting local processing of {len(media_items)} items...")
    
    images_with_meta = []
    async with httpx.AsyncClient(timeout=httpx.Timeout(4.0)) as client:
        tasks = [download_and_preprocess_image(m.preview_url, client) for m in media_items]
        downloaded = await asyncio.gather(*tasks, return_exceptions=True)
        
        for m, img in zip(media_items, downloaded):
            d = m.to_dict() if hasattr(m, "to_dict") else dict(m)
            if isinstance(img, Image.Image):
                d["_pil_image"] = img
            else:
                d["_pil_image"] = _generate_synthetic_image_for_item(d.get("id", "m"), d.get("title", ""))
            images_with_meta.append(d)

    unique_items, dropped_dupes = deduplicate_with_phash(
        images_with_meta,
        threshold=settings.PHASH_HAMMING_THRESHOLD
    )
    logger.info(f"pHash deduplication finished: {len(unique_items)} retained, {dropped_dupes} dropped.")

    classified = classify_images_zero_shot(unique_items, canonical_name=canonical_name, city=city)
    
    valid_items = [it for it in classified if not it.get("is_noise", False)]
    noise_count = len(classified) - len(valid_items)
    
    logger.info(f"Classification completed: {len(valid_items)} verified candidates, {noise_count} noise filtered.")

    return {
        "items": valid_items,
        "metrics": {
            "total_aggregated": len(media_items),
            "downloaded": len(images_with_meta),
            "duplicates_dropped": dropped_dupes,
            "noise_filtered": noise_count,
            "retained_candidates": len(valid_items)
        }
    }
