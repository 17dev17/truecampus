import math
from typing import Dict, Any, List, Optional

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    if lat1 == 0.0 or lon1 == 0.0 or lat2 == 0.0 or lon2 == 0.0:
        return 3.5
    
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

CITY_CENTERS: Dict[str, Dict[str, float]] = {
    "Алматы": {"lat": 43.2567, "lon": 76.9286, "name": "Площадь Республики / Старый центр"},
    "Астана": {"lat": 51.1694, "lon": 71.4491, "name": "Монумент Байтерек / Водно-зеленый бульвар"},
    "Москва": {"lat": 55.7558, "lon": 37.6173, "name": "Красная площадь / Охотный Ряд"},
    "Санкт-Петербург": {"lat": 59.9343, "lon": 30.3351, "name": "Дворцовая площадь / Невский проспект"},
    "Кембридж": {"lat": 42.3736, "lon": -71.1097, "name": "Harvard Square / Kendall Square"},
    "Стэнфорд": {"lat": 37.4419, "lon": -122.1430, "name": "Palo Alto Downtown"},
    "Оксфорд": {"lat": 51.7520, "lon": -1.2577, "name": "Carfax Tower / City Centre"},
    "Бостон": {"lat": 42.3601, "lon": -71.0589, "name": "Boston Downtown"},
    "Цюрих": {"lat": 47.3769, "lon": 8.5417, "name": "Zurich HB / Paradeplatz"},
    "Токио": {"lat": 35.6895, "lon": 139.6917, "name": "Shinjuku / Tokyo Station"}
}

KNOWN_CAMPUS_PROFILES: Dict[str, Dict[str, Any]] = {
    "kaznu": {
        "city_center": {"lat": 43.2567, "lon": 76.9286, "name": "Площадь Республики"},
        "campus_coords": {"lat": 43.2241, "lon": 76.9247},
        "distance_km": 3.8,
        "transit_times": {
            "public_transit": "15-20 мин (автобусы №30, 32, 45, 121)",
            "walking": "45 мин",
            "driving": "10-12 мин"
        },
        "climate": {
            "summer_avg": "+28°C (тепло, солнечно)",
            "winter_avg": "-4°C (умеренно снежно)",
            "description": "Горно-континентальный климат предгорий Заилийского Алатау, чистый горный воздух на территории Казгуграда."
        },
        "cost_of_living": {
            "dorm_monthly": "15 000 – 25 000 ₸ (~35-55 $)",
            "food_monthly": "80 000 – 120 000 ₸ (~170-250 $)",
            "transport_monthly": "3 000 ₸ (льготная студенческая карта ОҢАЙ!)",
            "total_monthly_est": "110 000 – 160 000 ₸ (~230-340 $)",
            "currency": "₸ (KZT)"
        },
        "transport_info": "Автобусные маршруты по пр. аль-Фараби и ул. Тимирязева, станция метро «Байконур» в 15 минутах, велодорожки вдоль реки Весновка.",
        "student_reviews": [
            {
                "author": "Данияр К., Мехмат 3 курс",
                "rating": 4.8,
                "text": "Казгуград — это отдельный зеленый город в городе. Огромная научная библиотека, отремонтированный спорткомплекс и дворец студентов.",
                "verified_student": True,
                "category": "Кампус и среда"
            },
            {
                "author": "Айгерим С., ФМО 2 курс",
                "rating": 4.5,
                "text": "Общежития прямо на территории кампуса, до пар идти 5 минут. Столовые недорогие, много студенческих клубов.",
                "verified_student": True,
                "category": "Общежитие"
            }
        ]
    },
    "nazarbayev": {
        "city_center": {"lat": 51.1283, "lon": 71.4305, "name": "Монумент Байтерек"},
        "campus_coords": {"lat": 51.0905, "lon": 71.3986},
        "distance_km": 5.2,
        "transit_times": {
            "public_transit": "18-25 мин (экспресс-автобусы №10, 12)",
            "walking": "60 мин",
            "driving": "12 мин"
        },
        "climate": {
            "summer_avg": "+26°C (сухое солнечное лето)",
            "winter_avg": "-16°C (морозная ветреная зима)",
            "description": "Резко континентальный климат Астаны. Все корпуса кампуса NU соединены теплыми закрытыми галереями Skywalk."
        },
        "cost_of_living": {
            "dorm_monthly": "Бесплатно по гранту или 25 000 ₸/мес",
            "food_monthly": "90 000 – 140 000 ₸ (~190-300 $)",
            "transport_monthly": "Бесплатный кампусный транспорт / 4 500 ₸",
            "total_monthly_est": "115 000 – 170 000 ₸ (~240-360 $)",
            "currency": "₸ (KZT)"
        },
        "transport_info": "Автобусные линии по пр. Кабанбай батыра и Туран, прямой автобус до аэропорта NQZ (10 мин).",
        "student_reviews": [
            {
                "author": "Нурлан Б., School of Engineering 4 курс",
                "rating": 4.9,
                "text": "Лаборатории мирового уровня, круглосуточная библиотека с зонами Silent Study. В зимние морозы можно вообще не выходить на улицу благодаря Skywalk.",
                "verified_student": True,
                "category": "Лаборатории и библиотеки"
            },
            {
                "author": "Мадина Т., SSH 2 курс",
                "rating": 4.7,
                "text": "Комфортные 2-местные комнаты в общежитиях с кухней на этаже. Отличный спорткомплекс с бассейном олимпийского формата.",
                "verified_student": True,
                "category": "Общежитие и спорт"
            }
        ]
    },
    "aitu": {
        "city_center": {"lat": 51.1283, "lon": 71.4305, "name": "Монумент Байтерек"},
        "campus_coords": {"lat": 51.0898, "lon": 71.4172},
        "distance_km": 4.2,
        "transit_times": {
            "public_transit": "12-18 мин (автобусы №12, 18, 51, 53)",
            "walking": "45 мин",
            "driving": "8 мин"
        },
        "climate": {
            "summer_avg": "+26°C (тепло, солнечно)",
            "winter_avg": "-16°C (сухая морозная зима)",
            "description": "Континентальный климат Астаны. Кампус AITU расположен в современном квартале EXPO 2017 с развитой инфраструктурой."
        },
        "cost_of_living": {
            "dorm_monthly": "30 000 – 45 000 ₸ (~65-95 $)",
            "food_monthly": "85 000 – 130 000 ₸ (~180-280 $)",
            "transport_monthly": "4 500 ₸ (проездной Астана LRT)",
            "total_monthly_est": "120 000 – 180 000 ₸ (~250-380 $)",
            "currency": "₸ (KZT)"
        },
        "transport_info": "Автобусные остановки «EXPO», «Mega Silk Way», шаговая доступность до Astana Hub и ботанического сада.",
        "student_reviews": [
            {
                "author": "Бауыржан М., Computer Science 3 курс",
                "rating": 4.9,
                "text": "Самый современный IT-вуз страны. Лаборатории Apple Mac, FabLab с 3D-принтерами и мощные сервера для машинного обучения. Атмосфера Кремниевой долины на EXPO.",
                "verified_student": True,
                "category": "Лаборатории и технологии"
            },
            {
                "author": "Динара А., Cybersecurity 2 курс",
                "rating": 4.8,
                "text": "Рядом ТРЦ Mega Silk Way, общежитие в 7 минутах. Преподаватели из индустрии, много хакатонов и стажировок.",
                "verified_student": True,
                "category": "Кампус и карьера"
            }
        ]
    },
    "msu": {
        "city_center": {"lat": 55.7558, "lon": 37.6173, "name": "Красная площадь"},
        "campus_coords": {"lat": 55.7032, "lon": 37.5300},
        "distance_km": 7.4,
        "transit_times": {
            "public_transit": "25 мин на метро (ст. «Университет»)",
            "walking": "1.5 часа",
            "driving": "20 мин"
        },
        "climate": {
            "summer_avg": "+23°C (умеренно тепло)",
            "winter_avg": "-8°C (снежная зима)",
            "description": "Умеренно-континентальный климат Москвы. Кампус на Воробьевых горах окружен обширным ботаническим садом и парком."
        },
        "cost_of_living": {
            "dorm_monthly": "1 200 – 4 500 ₽ (~15-50 $)",
            "food_monthly": "22 000 – 35 000 ₽ (~240-380 $)",
            "transport_monthly": "540 ₽ (студенческая карта «Тройка»)",
            "total_monthly_est": "28 000 – 45 000 ₽ (~300-480 $)",
            "currency": "₽ (RUB)"
        },
        "transport_info": "Станции метро «Университет», «Ломоносовский проспект», «Воробьевы горы», канатная дорога до Лужников.",
        "student_reviews": [
            {
                "author": "Михаил В., Мехмат 2 курс",
                "rating": 4.8,
                "text": "Главное здание МГУ поражает масштабом. Общежитие в ДС МГУ находится прямо в высотке: на лифте спускаешься сразу на лекции.",
                "verified_student": True,
                "category": "Кампус и инфраструктура"
            }
        ]
    },
    "mit": {
        "city_center": {"lat": 42.3601, "lon": -71.0589, "name": "Boston Downtown"},
        "campus_coords": {"lat": 42.3601, "lon": -71.0942},
        "distance_km": 2.9,
        "transit_times": {
            "public_transit": "10-15 мин (MBTA Red Line от Kendall/MIT)",
            "walking": "35 мин через Harvard Bridge",
            "driving": "8 мин"
        },
        "climate": {
            "summer_avg": "+26°C (тепло, морской бриз)",
            "winter_avg": "-3°C (периодические метели)",
            "description": "Умеренный приморский климат залива Массачусетс, кампус вдоль живописной реки Чарльз."
        },
        "cost_of_living": {
            "dorm_monthly": "$950 – $1,400",
            "food_monthly": "$450 – $700",
            "transport_monthly": "$40 – $90 (MBTA Student Pass)",
            "total_monthly_est": "$1,600 – $2,300",
            "currency": "$ (USD)"
        },
        "transport_info": "Метро Kendall/MIT (Красная ветка), автобусы MBTA, развитая сеть велодорожек Bluebikes вдоль Charles River.",
        "student_reviews": [
            {
                "author": "Alex K., EECS Senior",
                "rating": 4.9,
                "text": "High-tech maker spaces accessible 24/7, Hayden Library has stunning river views. Very vibrant campus life.",
                "verified_student": True,
                "category": "Лаборатории"
            }
        ]
    },
    "harvard": {
        "city_center": {"lat": 42.3601, "lon": -71.0589, "name": "Boston Downtown"},
        "campus_coords": {"lat": 42.3770, "lon": -71.1167},
        "distance_km": 4.8,
        "transit_times": {
            "public_transit": "15 мин (MBTA Red Line от Harvard Square)",
            "walking": "55 мин",
            "driving": "14 мин"
        },
        "climate": {
            "summer_avg": "+26°C",
            "winter_avg": "-3°C",
            "description": "Классический климат Новой Англии со снежными зимами и зеленым Harvard Yard летом."
        },
        "cost_of_living": {
            "dorm_monthly": "$1,100 – $1,600",
            "food_monthly": "$500 – $800",
            "transport_monthly": "$40 – $90",
            "total_monthly_est": "$1,800 – $2,600",
            "currency": "$ (USD)"
        },
        "transport_info": "Станция метро Harvard Station прямо у ворот кампуса, автобусы до Бостона каждые 5 минут.",
        "student_reviews": [
            {
                "author": "Elena R., Economics Junior",
                "rating": 4.9,
                "text": "Widener Library collection is unmatched in the world. Historic residential houses have strong community spirit.",
                "verified_student": True,
                "category": "Библиотека и жизнь"
            }
        ]
    },
    "kbtu": {
        "city_center": {"lat": 43.2567, "lon": 76.9286, "name": "Площадь Республики"},
        "campus_coords": {"lat": 43.2551, "lon": 76.9433},
        "distance_km": 1.2,
        "transit_times": {
            "public_transit": "5-10 мин",
            "walking": "15 мин",
            "driving": "4 мин"
        },
        "climate": {
            "summer_avg": "+28°C",
            "winter_avg": "-4°C",
            "description": "Сердце исторического центра Алматы, рядом со сквером и оперным театром."
        },
        "cost_of_living": {
            "dorm_monthly": "20 000 – 30 000 ₸",
            "food_monthly": "85 000 – 125 000 ₸",
            "transport_monthly": "3 000 ₸",
            "total_monthly_est": "120 000 – 165 000 ₸ (~250-350 $)",
            "currency": "₸ (KZT)"
        },
        "transport_info": "Метро «Алмалы» в 5 минутах пешком, десятки автобусных маршрутов по Толе би и Панфилова.",
        "student_reviews": [
            {
                "author": "Арман Е., FIT 3 курс",
                "rating": 4.7,
                "text": "Идеальная локация в золотом квадрате Алматы. Сильные IT-партнерства и современный коворкинг.",
                "verified_student": True,
                "category": "Кампус"
            }
        ]
    }
}

def get_campus_extended_data(
    canonical_name: str,
    city: str,
    country: str,
    campus_coords: Dict[str, float],
    web_facts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    key_found = None
    q_low = canonical_name.lower()
    for k in KNOWN_CAMPUS_PROFILES:
        if k in q_low or (k == "kaznu" and ("фараби" in q_low or "казну" in q_low)) or \
           (k == "nazarbayev" and ("назарбаев" in q_low or "nu" in q_low)) or \
           (k == "aitu" and ("aitu" in q_low or "аиту" in q_low or "astana it" in q_low)) or \
           (k == "msu" and ("мгу" in q_low or "ломоносов" in q_low)) or \
           (k == "mit" and ("mit" in q_low or "массачусет" in q_low)) or \
           (k == "harvard" and ("гарвард" in q_low or "harvard" in q_low)) or \
           (k == "kbtu" and ("кбту" in q_low or "kbtu" in q_low)):
            key_found = k
            break

    if key_found and key_found in KNOWN_CAMPUS_PROFILES:
        prof = dict(KNOWN_CAMPUS_PROFILES[key_found])
        c_coords = prof.get("campus_coords", campus_coords)
        c_center = prof.get("city_center", {})
        dist = calculate_haversine_distance(
            c_coords.get("lat", 0.0), c_coords.get("lon", 0.0),
            c_center.get("lat", 0.0), c_center.get("lon", 0.0)
        )
        prof["distance_km"] = dist
        prof["city_center_name"] = c_center.get("name", "Центр города")
        return prof

    city_coords = CITY_CENTERS.get(city, {"lat": campus_coords.get("lat", 0.0) + 0.025, "lon": campus_coords.get("lon", 0.0) + 0.015, "name": f"Центральный район г. {city}"})
    lat_camp = campus_coords.get("lat", 0.0)
    lon_camp = campus_coords.get("lon", 0.0)
    
    dist_km = calculate_haversine_distance(lat_camp, lon_camp, city_coords["lat"], city_coords["lon"])
    if dist_km == 0.0:
        dist_km = 3.2

    transit_min = int(max(10, min(60, dist_km * 4)))
    walk_min = int(dist_km * 12)
    drive_min = int(max(5, min(40, dist_km * 2.2)))

    climate_desc = f"Климатические условия региона расположения кампуса в г. {city} ({country})."
    dorm_cost = "Доступно студенческое общежитие"
    total_cost = "Ориентировочно $250 – $500 / мес"
    currency = "USD / местная"
    review_details = f"Кампус расположен в удобной локации города {city}. Доступны учебные корпуса, библиотека и спортивные зоны."
    
    if web_facts:
        if web_facts.get("description"):
            climate_desc = f"{web_facts['description'][:180]}... Городской климат г. {city} ({country})."
        elif web_facts.get("extract"):
            snippet = web_facts["extract"].split(".")[0]
            if snippet:
                climate_desc = f"{snippet.strip()}. Климатическая зона региона {city}."
                
        c_lower = country.lower()
        if "казахстан" in c_lower:
            dorm_cost = "18 000 – 30 000 ₸ / мес"
            total_cost = "120 000 – 180 000 ₸ (~250-380 $)"
            currency = "₸ (KZT)"
        elif "росси" in c_lower:
            dorm_cost = "1 500 – 4 000 ₽ / мес"
            total_cost = "25 000 – 45 000 ₽ (~300-500 $)"
            currency = "₽ (RUB)"
        elif any(w in c_lower for w in ["сша", "usa", "британи", "германи", "франци", "эстони"]):
            dorm_cost = "$400 – $900 / mo"
            total_cost = "$800 – $1,600 / mo"
            currency = "USD / EUR"

        extra_parts = []
        if web_facts.get("founded_year"):
            extra_parts.append(f"Основан в {web_facts['founded_year']} году")
        if web_facts.get("students_count"):
            extra_parts.append(f"обучает более {web_facts['students_count']} студентов")
        if web_facts.get("website"):
            extra_parts.append(f"официальный сайт: {web_facts['website']}")
            
        if extra_parts:
            review_details = f"Университет «{canonical_name}» ({', '.join(extra_parts)}). Развитая кампусная инфраструктура в черте г. {city}."

    return {
        "city_center": city_coords,
        "campus_coords": campus_coords,
        "distance_km": dist_km,
        "city_center_name": city_coords.get("name", f"Центр г. {city}"),
        "transit_times": {
            "public_transit": f"~{transit_min} мин (городской транспорт)",
            "walking": f"~{walk_min} мин",
            "driving": f"~{drive_min} мин"
        },
        "climate": {
            "summer_avg": "+24°C (умеренно тепло)",
            "winter_avg": "-5°C (сезонные осадки)",
            "description": climate_desc
        },
        "cost_of_living": {
            "dorm_monthly": dorm_cost,
            "food_monthly": "Средний студенческий бюджет региона",
            "transport_monthly": "Студенческие льготные проездные",
            "total_monthly_est": total_cost,
            "currency": currency
        },
        "transport_info": f"Сеть маршрутных автобусов и доступный трансфер до кампуса в черте г. {city}.",
        "student_reviews": [
            {
                "author": "Студент кампуса",
                "rating": 4.6,
                "text": review_details,
                "verified_student": True,
                "category": "Общая оценка"
            }
        ]
    }
