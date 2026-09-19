import os
import sys
import uuid
import logging
from typing import Dict, Any, Optional, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

from core.config import settings
from core.disambiguator import disambiguate_university, detect_ambiguity
from core.aggregator import aggregate_media
from core.processor import process_media_pipeline
from core.rules import apply_rule_engine
from core.summary import generate_campus_summary
from core.pdf_generator import build_pdf_report
from core.campus_data import get_campus_extended_data
from core.web_search import search_university_info
from core.auth_credits import auth_router, get_current_user_from_auth, ANALYSIS_COST_CREDITS, USERS_STORE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("truecampus.main")

app = FastAPI(
    title="TrueCampus API",
    description="AI Verification Engine for University Visual Campus & Student Life (LOCUS Hackathon 2026 Case 01)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

PROFILES_STORE: Dict[str, Dict[str, Any]] = {}

class AnalyzeRequest(BaseModel):
    query: str
    agency_name: Optional[str] = None
    contact_email: Optional[str] = None
    user_email: Optional[str] = None
    token: Optional[str] = None

class CompareRequest(BaseModel):
    query1: str
    query2: str

async def _run_analysis_pipeline(raw_query: str, agency_name: Optional[str] = None, contact_email: Optional[str] = None) -> Dict[str, Any]:
    disambiguated = await disambiguate_university(raw_query)
    canonical_name = disambiguated.get("canonical_name", raw_query)
    city = disambiguated.get("city", "Кампус")
    country = disambiguated.get("country", "Мир")
    coords = disambiguated.get("coordinates", {"lat": 0.0, "lon": 0.0})

    web_facts = {}
    try:
        web_facts = await search_university_info(canonical_name)
        if web_facts:
            if (coords.get("lat", 0.0) == 0.0 and coords.get("lon", 0.0) == 0.0) and (web_facts.get("coordinates", {}).get("lat", 0.0) != 0.0):
                coords = web_facts["coordinates"]
                disambiguated["coordinates"] = coords
            if (not city or city == "Кампус") and web_facts.get("city"):
                city = web_facts["city"]
                disambiguated["city"] = city
            if (not country or country == "Мир") and web_facts.get("country"):
                country = web_facts["country"]
                disambiguated["country"] = country
    except Exception as e:
        logger.warning(f"Step 1.5 web search enrichment error: {e}")

    media_items, sources_status = await aggregate_media(disambiguated)

    processing_results = await process_media_pipeline(media_items, canonical_name=canonical_name, city=city)

    rules_result = apply_rule_engine(processing_results["items"])

    campus_summary = await generate_campus_summary(disambiguated, rules_result, sources_status, web_search_facts=web_facts)

    campus_extended = get_campus_extended_data(canonical_name, city, country, coords, web_facts=web_facts)

    profile_id = str(uuid.uuid4())[:8]
    profile_data = {
        "profile_id": profile_id,
        "raw_query": raw_query,
        "canonical_name": canonical_name,
        "english_name": disambiguated.get("english_name", raw_query),
        "short_name": disambiguated.get("short_name", ""),
        "has_typo": disambiguated.get("has_typo", False),
        "did_you_mean": disambiguated.get("did_you_mean", canonical_name),
        "is_ambiguous": disambiguated.get("is_ambiguous", False),
        "candidates": disambiguated.get("candidates", []),
        "city": city,
        "country": country,
        "coordinates": coords,
        "disambiguation_source": disambiguated.get("disambiguation_source", "local"),
        "campus_summary": campus_summary,
        "sources_status": sources_status,
        "web_facts": web_facts,
        "metrics": processing_results["metrics"],
        "categories": rules_result["categories"],
        "rules_summary": rules_result["summary"],
        "campus_data": campus_extended,
        "agency_branding": {
            "name": agency_name or settings.branding.name,
            "contact_email": contact_email or settings.branding.contact_email
        }
    }

    PROFILES_STORE[profile_id] = profile_data
    return profile_data

@app.post("/api/analyze")
async def analyze_university(payload: AnalyzeRequest, authorization: Optional[str] = Header(None)):
    raw_query = payload.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    token = payload.token or authorization
    user = get_current_user_from_auth(token, payload.user_email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Регистрация обязательна! Пожалуйста, войдите или зарегистрируйтесь для анализа университета."
        )

    current_credits = user.get("credits", 0)
    if current_credits < ANALYSIS_COST_CREDITS:
        raise HTTPException(
            status_code=402,
            detail="Кредиты закончились! Пожалуйста, пополните баланс для продолжения проверок университетов."
        )

    user["credits"] = current_credits - ANALYSIS_COST_CREDITS
    logger.info(f"User '{user['email']}' spent {ANALYSIS_COST_CREDITS} credit for query: '{raw_query}'. Remaining: {user['credits']}")

    logger.info(f"Initiating TrueCampus pipeline for query: '{raw_query}'")
    profile = await _run_analysis_pipeline(raw_query, payload.agency_name, payload.contact_email)
    profile["user_remaining_credits"] = user["credits"]
    profile["user_email"] = user["email"]
    return profile

@app.get("/api/suggest")
async def suggest_university(q: str):
    q_clean = q.strip()
    if not q_clean:
        return {"has_typo": False, "did_you_mean": "", "canonical_name": "", "is_ambiguous": False, "candidates": []}
    
    disambiguated = await disambiguate_university(q_clean)
    return {
        "raw_query": q_clean,
        "has_typo": disambiguated.get("has_typo", False),
        "did_you_mean": disambiguated.get("did_you_mean", disambiguated.get("canonical_name", q_clean)),
        "canonical_name": disambiguated.get("canonical_name", q_clean),
        "city": disambiguated.get("city", ""),
        "country": disambiguated.get("country", ""),
        "is_ambiguous": disambiguated.get("is_ambiguous", False),
        "candidates": disambiguated.get("candidates", [])
    }

@app.get("/api/disambiguate")
async def disambiguate_query(q: str):
    q_clean = q.strip()
    candidates = detect_ambiguity(q_clean) or []
    return {
        "query": q_clean,
        "is_ambiguous": bool(candidates),
        "candidates": candidates
    }

@app.post("/api/compare")
async def compare_universities(payload: CompareRequest):
    q1 = payload.query1.strip()
    q2 = payload.query2.strip()
    if not q1 or not q2:
        raise HTTPException(status_code=400, detail="Both university queries must be provided")

    prof1 = await _run_analysis_pipeline(q1)
    prof2 = await _run_analysis_pipeline(q2)

    comp_matrix = {
        "univ1": {
            "profile_id": prof1["profile_id"],
            "name": prof1["canonical_name"],
            "short_name": prof1["short_name"],
            "city": f"{prof1['city']}, {prof1['country']}",
            "coverage_pct": prof1["rules_summary"]["verification_coverage_percent"],
            "verified_photos_count": prof1["rules_summary"]["total_verified_photos"],
            "trust_index": prof1["rules_summary"].get("overall_trust_index", 85),
            "distance_to_center_km": prof1["campus_data"]["distance_km"],
            "transit_time": prof1["campus_data"]["transit_times"]["public_transit"],
            "monthly_cost": prof1["campus_data"]["cost_of_living"]["total_monthly_est"],
            "climate": prof1["campus_data"]["climate"]["summer_avg"],
            "categories_verified_count": prof1["rules_summary"]["categories_verified"],
            "top_photos": [
                it["preview_url"] for cat in prof1["categories"].values() for it in cat["items"][:1]
            ][:4]
        },
        "univ2": {
            "profile_id": prof2["profile_id"],
            "name": prof2["canonical_name"],
            "short_name": prof2["short_name"],
            "city": f"{prof2['city']}, {prof2['country']}",
            "coverage_pct": prof2["rules_summary"]["verification_coverage_percent"],
            "verified_photos_count": prof2["rules_summary"]["total_verified_photos"],
            "trust_index": prof2["rules_summary"].get("overall_trust_index", 85),
            "distance_to_center_km": prof2["campus_data"]["distance_km"],
            "transit_time": prof2["campus_data"]["transit_times"]["public_transit"],
            "monthly_cost": prof2["campus_data"]["cost_of_living"]["total_monthly_est"],
            "climate": prof2["campus_data"]["climate"]["summer_avg"],
            "categories_verified_count": prof2["rules_summary"]["categories_verified"],
            "top_photos": [
                it["preview_url"] for cat in prof2["categories"].values() for it in cat["items"][:1]
            ][:4]
        }
    }

    return comp_matrix

@app.get("/api/profile/{profile_id}")
async def get_profile(profile_id: str):
    profile = PROFILES_STORE.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.get("/api/report/{profile_id}/pdf")
async def download_pdf_report(profile_id: str):
    profile = PROFILES_STORE.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    pdf_bytes = build_pdf_report(profile)
    ascii_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    safe_name = "".join([c for c in profile.get("short_name", "") if c in ascii_chars]) or "campus"
    filename = f"TrueCampus_Audit_{safe_name}_{profile_id}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.get("/api/report/{profile_id}/print", response_class=HTMLResponse)
async def view_print_report(profile_id: str):
    profile = PROFILES_STORE.get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    categories_html = ""
    for c_key, c_info in profile.get("categories", {}).items():
        is_v = c_info.get("is_verified")
        badge_cls = "badge-verified" if is_v else "badge-unverified"
        badge_text = f"ВЕРИФИЦИРОВАНО ({c_info.get('items_count', 0)} фото)" if is_v else "НЕТ ВЕРИФИЦИРОВАННЫХ ДАННЫХ"
        
        cards_html = ""
        for it in c_info.get("items", []):
            cards_html += f"""
            <div class="print-card">
                <img src="{it.get('preview_url')}" alt="{it.get('title')}" />
                <div class="print-card-body">
                    <strong>{it.get('title', '')[:30]}</strong>
                    <div>Достоверность: {it.get('trust_score', 80)}% ({it.get('trust_label', 'Подтверждено')})</div>
                    <div>Лицензия: <span class="badge-cc">{it.get('license_name', '')}</span></div>
                    <div class="small-text">Дата: {it.get('date_published', '')} | Автор: {it.get('author', '')[:25]}</div>
                </div>
            </div>
            """
        categories_html += f"""
        <section class="category-section">
            <div class="cat-header">
                <h2>{c_info.get('title', '')}</h2>
                <span class="badge {badge_cls}">{badge_text}</span>
            </div>
            <p class="cat-desc">{c_info.get('description', '')}</p>
            <div class="cards-grid">
                {cards_html if cards_html else '<p class="empty-text">Принцип честной неопределенности: нет подтвержденных снимков</p>'}
            </div>
        </section>
        """

    campus_data = profile.get("campus_data", {})
    cost_data = campus_data.get("cost_of_living", {})
    
    sources_html = ""
    for s_name, s_info in profile.get("sources_status", {}).items():
        st = "✅ Доступен" if s_info.get("status") == "ok" else "⚠️ Ограничен"
        sources_html += f"<li><strong>{s_name}:</strong> {st} ({s_info.get('count', 0)} элементов)</li>"

    agency_branding = profile.get("agency_branding", {})

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>TrueCampus Audit - {profile.get('canonical_name', '')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 40px; color: #1e293b; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 24px; }}
        .agency {{ text-align: right; color: #64748b; font-size: 14px; }}
        h1 {{ margin: 0 0 6px 0; color: #0f172a; }}
        .summary-box {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 4px; margin-bottom: 24px; font-style: italic; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .badge-verified {{ background: #dcfce7; color: #15803d; }}
        .badge-unverified {{ background: #fee2e2; color: #991b1b; }}
        .badge-cc {{ background: #e0e7ff; color: #3730a3; padding: 2px 6px; border-radius: 3px; font-size: 11px; }}
        .cat-header {{ display: flex; justify-content: space-between; align-items: center; margin-top: 20px; }}
        .cards-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }}
        .print-card {{ border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; }}
        .print-card img {{ width: 100%; height: 160px; object-fit: cover; }}
        .print-card-body {{ padding: 10px; font-size: 12px; }}
        .small-text {{ font-size: 11px; color: #64748b; }}
        .empty-text {{ color: #94a3b8; font-style: italic; }}
        .print-btn {{ margin-bottom: 20px; padding: 8px 16px; background: #2563eb; color: #fff; border: none; border-radius: 4px; cursor: pointer; }}
        .bonus-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; margin-bottom: 24px; }}
        @media print {{ .print-btn {{ display: none; }} }}
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">Печать / Сохранить в PDF</button>
    <div class="header">
        <div>
            <h1>{profile.get('canonical_name', '')}</h1>
            <div>{profile.get('english_name', '')} | {profile.get('city', '')}, {profile.get('country', '')}</div>
        </div>
        <div class="agency">
            <strong>{agency_branding.get('name', '')}</strong><br/>
            {agency_branding.get('contact_email', '')}
        </div>
    </div>
    
    <div class="summary-box">
        «{profile.get('campus_summary', '')}»
    </div>

    <div class="bonus-box">
        <h3>Городская среда и проживание</h3>
        <div><strong>Расстояние до центра:</strong> {campus_data.get('distance_km', '3.5')} км ({campus_data.get('transit_times', {}).get('public_transit', '20 мин')})</div>
        <div><strong>Климат:</strong> {campus_data.get('climate', {}).get('summer_avg', '')} | {campus_data.get('climate', {}).get('description', '')}</div>
        <div><strong>Ориентировочный бюджет:</strong> {cost_data.get('total_monthly_est', '')}</div>
    </div>

    <h3>Статус открытых источников данных</h3>
    <ul>{sources_html}</ul>

    {categories_html}
</body>
</html>"""
    return HTMLResponse(content=html_content)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

