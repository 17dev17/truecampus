import logging
from typing import List, Dict, Any, Tuple
from core.config import settings

logger = logging.getLogger("truecampus.rules")

ALLOWED_CC_LICENSES = [
    "cc0", "public domain", "cc by", "cc by-sa", "cc by 2.0", "cc by 3.0", "cc by 4.0",
    "cc by-sa 2.0", "cc by-sa 3.0", "cc by-sa 4.0", "mit", "apache"
]

def verify_legal_purity(item: Dict[str, Any]) -> Tuple[bool, str]:
    license_name = (item.get("license_name") or "").lower()
    source_url = item.get("source_url") or ""

    if not source_url:
        return False, "Отсутствует прямая ссылка на первоисточник"

    is_cc_clean = any(lic in license_name for lic in ALLOWED_CC_LICENSES)
    if not is_cc_clean and "cc" not in license_name:
        return False, f"Неподтвержденный тип лицензии ({item.get('license_name')})"

    return True, "Юридически чисто (CC License verified)"

def apply_rule_engine(processed_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    from core.processor import CATEGORIES
    threshold = settings.CONFIDENCE_THRESHOLD

    structured_categories: Dict[str, Dict[str, Any]] = {}
    
    for cat_key, cat_meta in CATEGORIES.items():
        structured_categories[cat_key] = {
            "key": cat_key,
            "title": cat_meta["title"],
            "description": cat_meta["description"],
            "is_verified": False,
            "status_text": "Нет верифицированных данных",
            "status_code": "unverified",
            "average_confidence": 0.0,
            "average_trust_score": 0,
            "items_count": 0,
            "items": [],
            "rejections": []
        }

    for item in processed_items:
        cat_key = item.get("category")
        if cat_key not in structured_categories:
            continue

        conf = float(item.get("confidence", 0.0))
        is_legal, legal_reason = verify_legal_purity(item)
        item["legal_verified"] = is_legal
        item["legal_status_text"] = legal_reason

        if not is_legal:
            structured_categories[cat_key]["rejections"].append({
                "id": item.get("id"),
                "reason": legal_reason,
                "confidence": conf
            })
            continue

        if conf >= threshold:
            structured_categories[cat_key]["items"].append(item)
        else:
            structured_categories[cat_key]["rejections"].append({
                "id": item.get("id"),
                "reason": f"Низкий порог доверия ({conf:.2f} < {threshold:.2f})",
                "confidence": conf
            })

    total_verified_photos = 0
    categories_verified_count = 0
    total_trust_pts = 0

    for cat_key, cat_data in structured_categories.items():
        count = len(cat_data["items"])
        cat_data["items_count"] = count
        
        if count > 0:
            avg_conf = sum(it["confidence"] for it in cat_data["items"]) / count
            avg_trust = int(sum(it.get("trust_score", int(it.get("confidence", 0.7)*100)) for it in cat_data["items"]) / count)
            cat_data["average_confidence"] = round(avg_conf, 3)
            cat_data["average_trust_score"] = avg_trust
            cat_data["is_verified"] = True
            cat_data["status_text"] = f"Верифицировано ({count} фото, точность {int(avg_conf * 100)}%)"
            cat_data["status_code"] = "verified"
            total_verified_photos += count
            categories_verified_count += 1
            total_trust_pts += avg_trust
        else:
            cat_data["is_verified"] = False
            cat_data["status_text"] = "Нет верифицированных данных"
            cat_data["status_code"] = "unverified"

    compliance_rate = round((categories_verified_count / len(CATEGORIES)) * 100, 1)
    overall_trust_index = int(total_trust_pts / categories_verified_count) if categories_verified_count > 0 else 0
    
    return {
        "categories": structured_categories,
        "summary": {
            "total_verified_photos": total_verified_photos,
            "categories_verified": categories_verified_count,
            "total_categories": len(CATEGORIES),
            "verification_coverage_percent": compliance_rate,
            "overall_trust_index": overall_trust_index,
            "honest_uncertainty_active": categories_verified_count < len(CATEGORIES)
        }
    }
