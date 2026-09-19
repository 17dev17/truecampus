import json
import logging
import re
import difflib
from typing import Dict, Any, List, Optional, Tuple
import httpx
from core.config import settings

logger = logging.getLogger("truecampus.disambiguator")

KNOWN_UNIVERSITIES: List[Dict[str, Any]] = [
    {
        "match_keys": ["казну", "аль-фараби", "аль фараби", "al-farabi", "farabi", "kaznu", "казахский национальный университет"],
        "canonical_name": "Казахский национальный университет имени аль-Фараби",
        "english_name": "Al-Farabi Kazakh National University",
        "short_name": "КазНУ / KazNU",
        "city": "Алматы",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["Al-Farabi Kazakh National University", "KazNU campus", "КазНУ городок", "Al-Farabi University Almaty", "Al-Farabi library"],
        "coordinates": {"lat": 43.2241, "lon": 76.9247}
    },
    {
        "match_keys": ["назарбаев", "nazarbayev", "nu", "ну", "nazarbayev university", "назарбаев университет"],
        "canonical_name": "Назарбаев Университет",
        "english_name": "Nazarbayev University",
        "short_name": "NU",
        "city": "Астана",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["Nazarbayev University", "NU campus Astana", "Nazarbayev University building", "NU atrium Astana"],
        "coordinates": {"lat": 51.0905, "lon": 71.3986}
    },
    {
        "match_keys": ["aitu", "аиту", "astana it", "astana it university", "астана ит", "астана it", "астана айти", "aitu university"],
        "canonical_name": "Astana IT University (Астана IT Университет)",
        "english_name": "Astana IT University",
        "short_name": "AITU",
        "city": "Астана",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["Astana IT University", "AITU campus Astana", "AITU EXPO building", "Astana IT University building"],
        "coordinates": {"lat": 51.0898, "lon": 71.4172}
    },
    {
        "match_keys": ["кимэп", "kimep", "кимеп", "kimep university"],
        "canonical_name": "Университет КИМЭП (KIMEP University)",
        "english_name": "KIMEP University",
        "short_name": "КИМЭП / KIMEP",
        "city": "Алматы",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["KIMEP University Almaty", "КИМЭП кампус", "KIMEP Abay Almaty"],
        "coordinates": {"lat": 43.2432, "lon": 76.9548}
    },
    {
        "match_keys": ["муит", "iitu", "ииту", "международный университет информационных технологий"],
        "canonical_name": "Международный университет информационных технологий (МУИТ / IITU)",
        "english_name": "International Information Technology University",
        "short_name": "МУИТ / IITU",
        "city": "Алматы",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["IITU University Almaty", "МУИТ Алматы", "International Information Technology University"],
        "coordinates": {"lat": 43.2351, "lon": 76.9094}
    },
    {
        "match_keys": ["кбту", "kbtu", "казахстанско-британский", "kazakh-british"],
        "canonical_name": "Казахстанско-Британский технический университет",
        "english_name": "Kazakh-British Technical University",
        "short_name": "КБТУ / KBTU",
        "city": "Алматы",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["Kazakh-British Technical University", "KBTU Almaty building", "КБТУ Толе би", "KBTU facade"],
        "coordinates": {"lat": 43.2551, "lon": 76.9433}
    },
    {
        "match_keys": ["сатпаев", "сатпаева", "satbayev", "казниту", "политех алматы", "казпти", "satbayev university"],
        "canonical_name": "Satbayev University (КазНИТУ имени К. И. Сатпаева)",
        "english_name": "Satbayev University",
        "short_name": "Satbayev University",
        "city": "Алматы",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["Satbayev University", "КазНИТУ Сатпаева", "Satbayev University campus Almaty"],
        "coordinates": {"lat": 43.2372, "lon": 76.9318}
    },
    {
        "match_keys": ["ену", "гумилева", "гумилев", "enu", "евразийский национальный"],
        "canonical_name": "Евразийский национальный университет имени Л. Н. Гумилёва",
        "english_name": "L.N. Gumilyov Eurasian National University",
        "short_name": "ЕНУ / ENU",
        "city": "Астана",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["Eurasian National University Astana", "ЕНУ Гумилева Астана", "ENU campus"],
        "coordinates": {"lat": 51.1605, "lon": 71.4647}
    },
    {
        "match_keys": ["сду", "sdu", "демиреля", "сулейман демирель", "suleyman demirel university"],
        "canonical_name": "Университет имени Сулеймана Демиреля",
        "english_name": "Suleyman Demirel University",
        "short_name": "SDU",
        "city": "Алматы (Каскелен)",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["SDU University Kaskelen", "SDU campus Almaty", "СДУ университет"],
        "coordinates": {"lat": 43.2081, "lon": 76.6698}
    },
    {
        "match_keys": ["казнму", "асфендиярова", "асфендияров", "kaznmu", "медицинский алматы"],
        "canonical_name": "Казахский национальный медицинский университет имени С. Д. Асфендиярова",
        "english_name": "Asfendiyarov Kazakh National Medical University",
        "short_name": "КазНМУ / KazNMU",
        "city": "Алматы",
        "country": "Казахстан",
        "country_code": "KZ",
        "search_keywords": ["KazNMU Almaty", "КазНМУ Асфендиярова", "Kazakh National Medical University"],
        "coordinates": {"lat": 43.2508, "lon": 76.9334}
    },
    {
        "match_keys": ["мгу", "ломоносова", "ломоносов", "ломоносав", "msu", "lomonosov", "московский государственный"],
        "canonical_name": "Московский государственный университет имени М. В. Ломоносова",
        "english_name": "Lomonosov Moscow State University",
        "short_name": "МГУ / MSU",
        "city": "Москва",
        "country": "Россия",
        "country_code": "RU",
        "search_keywords": ["Moscow State University main building", "MSU campus", "МГУ Воробьевы горы", "MSU library"],
        "coordinates": {"lat": 55.7032, "lon": 37.5300}
    },
    {
        "match_keys": ["спбгу", "спб гу", "spbu", "санкт-петербургский государственный"],
        "canonical_name": "Санкт-Петербургский государственный университет",
        "english_name": "Saint Petersburg State University",
        "short_name": "СПбГУ / SPbU",
        "city": "Санкт-Петербург",
        "country": "Россия",
        "country_code": "RU",
        "search_keywords": ["Saint Petersburg State University", "SPbU campus", "Двенадцать коллегий СПбГУ"],
        "coordinates": {"lat": 59.9416, "lon": 30.2995}
    },
    {
        "match_keys": ["вшэ", "вышка", "hse", "higher school of economics", "высшая школа экономики"],
        "canonical_name": "Национальный исследовательский университет «Высшая школа экономики»",
        "english_name": "HSE University",
        "short_name": "НИУ ВШЭ / HSE",
        "city": "Москва",
        "country": "Россия",
        "country_code": "RU",
        "search_keywords": ["HSE University Moscow Pokrovsky", "НИУ ВШЭ Покровка", "HSE campus"],
        "coordinates": {"lat": 55.7541, "lon": 37.6489}
    },
    {
        "match_keys": ["мфти", "физтех", "mipt", "московский физико-технический"],
        "canonical_name": "Московский физико-технический институт (МФТИ)",
        "english_name": "Moscow Institute of Physics and Technology",
        "short_name": "МФТИ / MIPT",
        "city": "Москва (Долгопрудный)",
        "country": "Россия",
        "country_code": "RU",
        "search_keywords": ["MIPT campus Dolgoprudny", "МФТИ Физтех", "Moscow Institute of Physics and Technology"],
        "coordinates": {"lat": 55.9301, "lon": 37.5181}
    },
    {
        "match_keys": ["итмо", "itmo", "университет итмо"],
        "canonical_name": "Национальный исследовательский университет ИТМО",
        "english_name": "ITMO University",
        "short_name": "ИТМО / ITMO",
        "city": "Санкт-Петербург",
        "country": "Россия",
        "country_code": "RU",
        "search_keywords": ["ITMO University Saint Petersburg", "ИТМО Кронверкский", "ITMO campus"],
        "coordinates": {"lat": 59.9575, "lon": 30.3082}
    },
    {
        "match_keys": ["mit", "мит", "массачусетский", "massachusetts institute of technology"],
        "canonical_name": "Массачусетский технологический институт",
        "english_name": "Massachusetts Institute of Technology",
        "short_name": "MIT",
        "city": "Кембридж / Бостон",
        "country": "США",
        "country_code": "US",
        "search_keywords": ["Massachusetts Institute of Technology", "MIT campus", "MIT dome", "MIT Great Dome"],
        "coordinates": {"lat": 42.3601, "lon": -71.0942}
    },
    {
        "match_keys": ["гарвард", "harvard", "harvard university"],
        "canonical_name": "Гарвардский университет",
        "english_name": "Harvard University",
        "short_name": "Harvard",
        "city": "Кембридж / Бостон",
        "country": "США",
        "country_code": "US",
        "search_keywords": ["Harvard University campus", "Harvard Yard", "Harvard classrooms", "Widener Library Harvard"],
        "coordinates": {"lat": 42.3770, "lon": -71.1167}
    },
    {
        "match_keys": ["стэнфорд", "stanford", "стэнфордский", "stanford university"],
        "canonical_name": "Стэнфордский университет",
        "english_name": "Stanford University",
        "short_name": "Stanford",
        "city": "Стэнфорд / Пало-Альто",
        "country": "США",
        "country_code": "US",
        "search_keywords": ["Stanford University campus", "Stanford main quad", "Stanford University library", "Hoover Tower Stanford"],
        "coordinates": {"lat": 37.4275, "lon": -122.1697}
    },
    {
        "match_keys": ["оксфорд", "oxford", "oxford university"],
        "canonical_name": "Оксфордский университет",
        "english_name": "University of Oxford",
        "short_name": "Oxford",
        "city": "Оксфорд",
        "country": "Великобритания",
        "country_code": "GB",
        "search_keywords": ["University of Oxford campus", "Oxford colleges", "Bodleian library", "Radcliffe Camera Oxford"],
        "coordinates": {"lat": 51.7548, "lon": -1.2544}
    },
    {
        "match_keys": ["кембридж", "cambridge", "university of cambridge"],
        "canonical_name": "Кембриджский университет",
        "english_name": "University of Cambridge",
        "short_name": "Cambridge",
        "city": "Кембридж",
        "country": "Великобритания",
        "country_code": "GB",
        "search_keywords": ["University of Cambridge campus", "Cambridge King's College", "Cambridge library", "Trinity College Cambridge"],
        "coordinates": {"lat": 52.2043, "lon": 0.1218}
    },
    {
        "match_keys": ["eth", "етх", "цюрих", "eth zurich", "швейцарская высшая техническая"],
        "canonical_name": "Швейцарская высшая техническая школа Цюриха (ETH Zurich)",
        "english_name": "ETH Zurich",
        "short_name": "ETH Zurich",
        "city": "Цюрих",
        "country": "Швейцария",
        "country_code": "CH",
        "search_keywords": ["ETH Zurich main building", "ETH Zurich campus Zentrum", "ETH Hönggerberg"],
        "coordinates": {"lat": 47.3763, "lon": 8.5481}
    }
]

AMBIGUOUS_QUERY_CLUSTERS: Dict[str, List[Dict[str, str]]] = {
    "политех": [
        {"canonical_name": "Satbayev University (КазНИТУ имени К. И. Сатпаева)", "city": "Алматы, Казахстан", "short_name": "Satbayev University"},
        {"canonical_name": "Санкт-Петербургский политехнический университет Петра Великого", "city": "Санкт-Петербург, Россия", "short_name": "СПбПУ"},
        {"canonical_name": "Московский политехнический университет (Мосполитех)", "city": "Москва, Россия", "short_name": "Московский Политех"}
    ],
    "медицинский": [
        {"canonical_name": "Казахский национальный медицинский университет имени С. Д. Асфендиярова", "city": "Алматы, Казахстан", "short_name": "КазНМУ"},
        {"canonical_name": "Первый МГМУ имени И. М. Сеченова (Сеченовский Университет)", "city": "Москва, Россия", "short_name": "Сеченовский"},
        {"canonical_name": "Медицинский университет Астана (МУА)", "city": "Астана, Казахстан", "short_name": "МУА"}
    ],
    "кембридж": [
        {"canonical_name": "Кембриджский университет (University of Cambridge)", "city": "Кембридж, Великобритания", "short_name": "Cambridge UK"},
        {"canonical_name": "Массачусетский технологический институт (MIT)", "city": "Кембридж (Массачусетс), США", "short_name": "MIT Cambridge"},
        {"canonical_name": "Гарвардский университет (Harvard University)", "city": "Кембридж (Массачусетс), США", "short_name": "Harvard Cambridge"}
    ],
    "государственный университет": [
        {"canonical_name": "Казахский национальный университет имени аль-Фараби", "city": "Алматы, Казахстан", "short_name": "КазНУ"},
        {"canonical_name": "Московский государственный университет имени М. В. Ломоносова", "city": "Москва, Россия", "short_name": "МГУ"},
        {"canonical_name": "Санкт-Петербургский государственный университет", "city": "Санкт-Петербург, Россия", "short_name": "СПбГУ"}
    ]
}

def detect_ambiguity(query: str) -> Optional[List[Dict[str, str]]]:
    q_low = query.lower().strip()
    for cluster_key, candidates in AMBIGUOUS_QUERY_CLUSTERS.items():
        if cluster_key in q_low or q_low in cluster_key:
            return candidates
    return None

async def search_university_online_wikipedia(query: str) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=3.5, follow_redirects=True) as client:
            headers = {"User-Agent": "TrueCampusUniversitySearch/1.0"}
            
            url_ru = "https://ru.wikipedia.org/w/api.php"
            params_ru = {
                "action": "opensearch",
                "search": query,
                "limit": 5,
                "namespace": 0,
                "format": "json"
            }
            resp_ru = await client.get(url_ru, params=params_ru, headers=headers)
            if resp_ru.status_code == 200:
                data = resp_ru.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                for idx, title in enumerate(titles):
                    t_lower = title.lower()
                    if any(w in t_lower for w in ["университет", "институт", "академия", "колледж", "university", "college", "institute"]):
                        return {
                            "canonical_name": title,
                            "english_name": title,
                            "short_name": title,
                            "city": "Кампус",
                            "country": "Мир",
                            "country_code": "XX",
                            "search_keywords": [f"{title} campus", f"{title} university", title],
                            "coordinates": {"lat": 0.0, "lon": 0.0},
                            "disambiguation_source": "wikipedia_online_search",
                            "source_url": urls[idx] if idx < len(urls) else ""
                        }

            url_en = "https://en.wikipedia.org/w/api.php"
            params_en = {
                "action": "opensearch",
                "search": query,
                "limit": 5,
                "namespace": 0,
                "format": "json"
            }
            resp_en = await client.get(url_en, params=params_en, headers=headers)
            if resp_en.status_code == 200:
                data_en = resp_en.json()
                titles_en = data_en[1] if len(data_en) > 1 else []
                urls_en = data_en[3] if len(data_en) > 3 else []
                for idx, title in enumerate(titles_en):
                    t_lower = title.lower()
                    if any(w in t_lower for w in ["university", "college", "institute", "polytechnic"]):
                        return {
                            "canonical_name": title,
                            "english_name": title,
                            "short_name": title,
                            "city": "Campus City",
                            "country": "Global",
                            "country_code": "XX",
                            "search_keywords": [f"{title} campus", f"{title} building", title],
                            "coordinates": {"lat": 0.0, "lon": 0.0},
                            "disambiguation_source": "wikipedia_online_search_en",
                            "source_url": urls_en[idx] if idx < len(urls_en) else ""
                        }
    except Exception as e:
        logger.debug(f"Online Wikipedia search skipped/failed: {e}")
    return None

KNOWN_TYPOS: Dict[str, str] = {
    "козну": "Казахский национальный университет имени аль-Фараби",
    "казну аль фараби": "Казахский национальный университет имени аль-Фараби",
    "казну альфараби": "Казахский национальный университет имени аль-Фараби",
    "назарбаив": "Назарбаев Университет",
    "назербаев": "Назарбаев Университет",
    "назарбай": "Назарбаев Университет",
    "харвард": "Гарвардский университет",
    "хварвард": "Гарвардский университет",
    "гарворд": "Гарвардский университет",
    "харворд": "Гарвардский университет",
    "стенфорд": "Стэнфордский университет",
    "станфорд": "Стэнфордский университет",
    "стэндфорд": "Стэнфордский университет",
    "аксфорд": "Оксфордский университет",
    "оксфорт": "Оксфордский университет",
    "мгу ламаносава": "МГУ имени М.В. Ломоносова",
    "мгу ламоносов": "МГУ имени М.В. Ломоносова",
    "айту": "Astana IT University (Астана IT Университет)",
    "аиту уневерситет": "Astana IT University (Астана IT Университет)",
    "астана айти уневерситет": "Astana IT University (Астана IT Университет)",
}

def check_has_typo(raw_query: str, canonical_name: str, english_name: str = "", short_name: str = "", match_keys: Optional[List[str]] = None) -> Tuple[bool, str]:
    raw_clean = raw_query.strip().lower()
    norm_raw = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', raw_clean)
    
    for typo_key, canon_target in KNOWN_TYPOS.items():
        norm_typo = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', typo_key)
        if norm_raw == norm_typo or typo_key in raw_clean:
            return True, canon_target

    norm_canon = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', canonical_name.lower())
    norm_en = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', english_name.lower())
    norm_short = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', short_name.lower())
    
    if match_keys:
        for mk in match_keys:
            norm_mk = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', mk.lower())
            if norm_raw == norm_mk or (len(norm_raw) >= 3 and norm_raw in norm_mk) or (len(norm_mk) >= 3 and norm_mk in norm_raw):
                return False, canonical_name

    if norm_raw in (norm_canon, norm_en, norm_short):
        return False, canonical_name

    if norm_canon.startswith(norm_raw) or (norm_en and norm_en.startswith(norm_raw)):
        return False, canonical_name

    if len(norm_raw) >= 4 and (norm_raw in norm_canon or (norm_en and norm_raw in norm_en)):
        return False, canonical_name

    ratio_canon = difflib.SequenceMatcher(None, norm_raw, norm_canon).ratio()
    ratio_en = difflib.SequenceMatcher(None, norm_raw, norm_en).ratio() if norm_en else 0.0
    
    if max(ratio_canon, ratio_en) >= 0.78:
        return True, canonical_name

    return False, canonical_name

async def disambiguate_university(raw_query: str) -> Dict[str, Any]:
    raw_query = raw_query.strip()
    if not raw_query:
        raise ValueError("University query cannot be empty")

    cleaned = raw_query.lower().strip()
    cleaned_norm = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', cleaned)
    api_key = settings.GROQ_API_KEY
    result: Optional[Dict[str, Any]] = None

    for typo_key, target_canon in KNOWN_TYPOS.items():
        norm_typo = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', typo_key)
        if cleaned_norm == norm_typo or typo_key in cleaned:
            for item in KNOWN_UNIVERSITIES:
                if item["canonical_name"] == target_canon or target_canon in item["canonical_name"]:
                    res = {k: v for k, v in item.items() if k != "match_keys"}
                    res["disambiguation_source"] = "local_knowledge_base"
                    res["raw_query"] = raw_query
                    res["has_typo"] = True
                    res["did_you_mean"] = target_canon
                    res["is_ambiguous"] = False
                    res["candidates"] = []
                    return res

    ambiguous_candidates = detect_ambiguity(raw_query)

    matched_item_keys: List[str] = []
    for item in KNOWN_UNIVERSITIES:
        for key in item["match_keys"]:
            norm_k = re.sub(r'[^a-zA-Zа-яА-Я0-9]', '', key.lower())
            if key in cleaned or cleaned in key or norm_k == cleaned_norm:
                res = {k: v for k, v in item.items() if k != "match_keys"}
                res["disambiguation_source"] = "local_knowledge_base"
                result = res
                matched_item_keys = item["match_keys"]
                break
        if result:
            break

    if not result and api_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=api_key)
            prompt = f"""You are an advanced educational entity search engine with typo correction.
The user entered this university query: "{raw_query}".
Determine if there are typos, misspellings, slang or colloquial variations.
Respond ONLY with a valid JSON object:
{{
  "canonical_name": "Official Russian/native name of the university",
  "english_name": "Official English name",
  "short_name": "Acronym/abbreviation",
  "city": "City",
  "country": "Country",
  "country_code": "2-letter ISO code",
  "has_typo": false,
  "did_you_mean": "Official correct full name",
  "search_keywords": ["keyword 1", "keyword 2"],
  "coordinates": {{"lat": 0.0, "lon": 0.0}}
}}"""
            response = await client.chat.completions.create(
                model="llama-3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a precise JSON university entity search engine."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=320
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].startswith("```"): lines = lines[:-1]
                content = "\n".join(lines).strip()
            result = json.loads(content)
            result["disambiguation_source"] = "groq_llama_3_8b"
        except Exception as e:
            logger.warning(f"Groq disambiguation failed: {e}. Switching to online search.")

    if result and result.get("disambiguation_source") == "groq_llama_3_8b":
        try:
            from core.web_search import search_university_info
            web_facts = await search_university_info(result.get("canonical_name", raw_query))
            if web_facts:
                coords = result.get("coordinates", {})
                web_coords = web_facts.get("coordinates", {})
                if (coords.get("lat", 0.0) == 0.0 and coords.get("lon", 0.0) == 0.0) and (web_coords.get("lat", 0.0) != 0.0):
                    result["coordinates"] = web_coords
                if (not result.get("city") or result.get("city") == "Кампус") and web_facts.get("city"):
                    result["city"] = web_facts["city"]
                if (not result.get("country") or result.get("country") == "Мир") and web_facts.get("country"):
                    result["country"] = web_facts["country"]
                if web_facts.get("description"):
                    result["description"] = web_facts["description"]
                if web_facts.get("founded_year"):
                    result["founded_year"] = web_facts["founded_year"]
                if web_facts.get("website"):
                    result["website"] = web_facts["website"]
                if web_facts.get("students_count"):
                    result["students_count"] = web_facts["students_count"]
                if web_facts.get("sources"):
                    result["sources"] = web_facts["sources"]
        except Exception as e:
            logger.debug(f"Web search enrichment for Groq result failed: {e}")

    if not result:
        try:
            from core.web_search import search_university_info
            web_facts = await search_university_info(raw_query)
            if web_facts and (web_facts.get("canonical_name") or web_facts.get("extract")):
                c_name = web_facts.get("canonical_name") or raw_query.strip().title()
                en_name = web_facts.get("english_name") or c_name
                c_code = "KZ" if "Казахстан" in web_facts.get("country", "") else ("RU" if "Россия" in web_facts.get("country", "") else "XX")
                result = {
                    "canonical_name": c_name,
                    "english_name": en_name,
                    "short_name": raw_query.strip(),
                    "city": web_facts.get("city") or "Кампус",
                    "country": web_facts.get("country") or "Мир",
                    "country_code": c_code,
                    "search_keywords": [
                        f"{c_name} campus",
                        f"{en_name} campus building",
                        f"{c_name} university"
                    ],
                    "coordinates": web_facts.get("coordinates", {"lat": 0.0, "lon": 0.0}),
                    "description": web_facts.get("description", ""),
                    "founded_year": web_facts.get("founded_year"),
                    "students_count": web_facts.get("students_count"),
                    "website": web_facts.get("website"),
                    "disambiguation_source": "web_search",
                    "sources": web_facts.get("sources", [])
                }
        except Exception as e:
            logger.debug(f"Web search step failed: {e}")

    if not result:
        online_res = await search_university_online_wikipedia(raw_query)
        if online_res:
            result = online_res

    if not result:
        title_norm = raw_query.strip().title()
        en_query = raw_query.strip()
        result = {
            "canonical_name": title_norm if "университет" in cleaned or "university" in cleaned else f"{title_norm} University",
            "english_name": en_query if "university" in en_query.lower() else f"{en_query} University",
            "short_name": raw_query.strip(),
            "city": "Кампус",
            "country": "Мир",
            "country_code": "XX",
            "search_keywords": [
                f"{raw_query.strip()} university campus",
                f"{raw_query.strip()} campus building",
                f"{raw_query.strip()} university"
            ],
            "coordinates": {"lat": 0.0, "lon": 0.0},
            "disambiguation_source": "heuristic_fallback"
        }

    canon = result.get("canonical_name", raw_query)
    is_local = result.get("disambiguation_source") == "local_knowledge_base"

    if is_local:
        has_typo = False
        dym = canon
    else:
        has_typo, dym = check_has_typo(
            raw_query,
            canon,
            result.get("english_name", ""),
            result.get("short_name", ""),
            match_keys=matched_item_keys
        )
    
    result["raw_query"] = raw_query
    result["has_typo"] = bool(has_typo)
    result["did_you_mean"] = dym if has_typo else canon
    result["is_ambiguous"] = bool(ambiguous_candidates)
    result["candidates"] = ambiguous_candidates or []

    return result
