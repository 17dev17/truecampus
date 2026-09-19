import logging
from typing import Dict, Any, Optional
from core.config import settings

logger = logging.getLogger("truecampus.summary")

def _generate_rule_based_summary(
    canonical_name: str,
    city: str,
    country: str,
    categories: Dict[str, Any],
    sources_status: Dict[str, str],
    web_search_facts: Optional[Dict[str, Any]] = None
) -> str:
    verified_cats = []
    unverified_cats = []
    
    cat_names = {
        "campus": "учебных корпусов",
        "dormitory": "студенческих общежитий",
        "lecture_hall": "учебных аудиторий",
        "library": "научных библиотек",
        "city": "городской среды",
        "sport": "спортивных комплексов",
        "labs": "исследовательских лабораторий",
        "student_life": "студенческой жизни"
    }
    
    for k, info in categories.items():
        count = info.get("items_count", 0)
        cname = cat_names.get(k, k)
        if info.get("is_verified", False) and count > 0:
            verified_cats.append(f"{cname} ({count} фото)")
        else:
            unverified_cats.append(cname)

    loc_str = f"в г. {city}, {country}" if city and city != "Кампус" and city != "Unknown City" else f"({country})"
    
    lines = [
        f"Университет «{canonical_name}» расположен {loc_str}."
    ]

    if web_search_facts and web_search_facts.get("founded_year"):
        lines.append(f"Вуз основан в {web_search_facts['founded_year']} году.")
    
    if verified_cats:
        lines.append(f"По результатам локального аудита открытых медиа подтверждено наличие снимков: {', '.join(verified_cats)}.")
    else:
        lines.append("На текущий момент в открытых репозиториях не обнаружено изображений с достаточным уровнем уверенности.")
        
    if unverified_cats:
        lines.append(f"В рамках принципа честной неопределенности статус «Нет верифицированных данных» присвоен категориям: {', '.join(unverified_cats)}.")
    else:
        lines.append("Все ключевые категории визуального профиля успешно подтверждены открытыми лицензиями Creative Commons.")
        
    return " ".join(lines)

async def generate_campus_summary(
    disambiguated: Dict[str, Any],
    rules_result: Dict[str, Any],
    sources_status: Dict[str, str],
    web_search_facts: Optional[Dict[str, Any]] = None
) -> str:
    canonical_name = disambiguated.get("canonical_name", "Университет")
    city = disambiguated.get("city", "")
    country = disambiguated.get("country", "")
    categories = rules_result.get("categories", {})
    summary_meta = rules_result.get("summary", {})

    api_key = settings.GROQ_API_KEY
    if not api_key:
        logger.info("GROQ_API_KEY is not set. Generating deterministic campus summary.")
        return _generate_rule_based_summary(canonical_name, city, country, categories, sources_status, web_search_facts)

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key)
        
        category_stats = []
        for k, info in categories.items():
            status = "ВЕРИФИЦИРОВАНО" if info.get("is_verified") else "НЕТ ДАННЫХ"
            category_stats.append(f"- {info.get('title')}: {info.get('items_count')} фото [{status}]")
            
        category_stats_str = "\n".join(category_stats)
        active_sources = [k for k, v in sources_status.items() if "ok" in v.lower() or "loaded" in v.lower()]
        
        facts_summary = []
        if web_search_facts:
            if web_search_facts.get("description"):
                facts_summary.append(f"- Описание: {web_search_facts['description']}")
            if web_search_facts.get("founded_year"):
                facts_summary.append(f"- Год основания: {web_search_facts['founded_year']}")
            if web_search_facts.get("students_count"):
                facts_summary.append(f"- Число студентов: {web_search_facts['students_count']}")
            if web_search_facts.get("website"):
                facts_summary.append(f"- Официальный веб-сайт: {web_search_facts['website']}")
        web_facts_str = "\n".join(facts_summary) if facts_summary else "- Дополнительные интернет-факты не обнаружены"

        prompt = f"""Сформируй краткое, честное и объективное описание кампуса университета на русском языке (2-4 предложения) для абитуриента и экспертного жюри.
Используй ТОЛЬКО проверенные факты из предоставленных метаданных:
- Университет: {canonical_name}
- Локация: {city}, {country}
- Статус источников: {', '.join(active_sources) if active_sources else 'Открытые архивы'}
- Факты из интернет-поиска (web_search_facts):
{web_facts_str}
- Статистика по категориям:
{category_stats_str}
- Всего подтвержденных фото: {summary_meta.get('total_verified_photos', 0)}
- Принцип честной неопределенности: Если по какой-то категории нет данных (например, общежития или лаборатории), прямо укажи это.

Текст описания:"""

        response = await client.chat.completions.create(
            model="llama-3-8b-8192",
            messages=[
                {"role": "system", "content": "Ты аналитический ассистент сервиса верификации TrueCampus. Отвечай объективно, честно и кратко."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=240
        )
        
        content = response.choices[0].message.content.strip()
        return content
        
    except Exception as e:
        logger.warning(f"Groq summary generation failed: {e}. Using deterministic fallback.")
        return _generate_rule_based_summary(canonical_name, city, country, categories, sources_status, web_search_facts)
