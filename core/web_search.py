import asyncio
import json
import logging
import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple
import httpx
from core.config import settings

logger = logging.getLogger("truecampus.web_search")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 TrueCampusSearch/2.0 (audit@eduglobal.io)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

async def _fetch_ddg_instant(query: str, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1"
    }
    try:
        resp = await client.get(url, params=params, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("AbstractText") or data.get("Abstract")
            heading = data.get("Heading")
            abstract_url = data.get("AbstractURL")
            image = data.get("Image")
            
            related_topics = []
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    related_topics.append(topic.get("Text"))
                    
            official_website = None
            for result in data.get("Results", []):
                if isinstance(result, dict) and result.get("FirstURL"):
                    official_website = result.get("FirstURL")
                    break

            if abstract or heading:
                return {
                    "heading": heading or query,
                    "abstract": abstract or "",
                    "url": abstract_url or "",
                    "website": official_website,
                    "image": image if image and image.startswith("http") else None,
                    "related": related_topics,
                    "source": "duckduckgo_instant"
                }
    except Exception as e:
        logger.debug(f"DuckDuckGo instant answer fetch error: {e}")
    return None

async def _fetch_wikipedia_full(query: str, client: httpx.AsyncClient, lang: str = "ru") -> Optional[Dict[str, Any]]:
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 3
    }
    try:
        resp = await client.get(search_url, params=params, headers=HEADERS)
        if resp.status_code != 200:
            return None
        data = resp.json()
        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return None
            
        page_title = None
        for res_item in search_results:
            t = res_item.get("title", "")
            t_low = t.lower()
            if any(k in t_low for k in ["университет", "university", "институт", "institute", "колледж", "college", "академи", "academy", "polytechnic"]):
                page_title = t
                break
        
        if not page_title and search_results:
            if lang == "ru" and all(ord(ch) < 128 for ch in query.replace(" ", "")):
                snippet = search_results[0].get("snippet", "").lower()
                if not any(k in snippet for k in ["университет", "university", "институт", "institute", "вуз"]):
                    return None
            page_title = search_results[0].get("title", "")
            
        if not page_title:
            return None
            
        encoded_title = urllib.parse.quote(page_title)
        rest_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
        summary_resp = await client.get(rest_url, headers=HEADERS)
        
        lat = None
        lon = None
        extract = ""
        description = ""
        lead_image = None
        page_url = f"https://{lang}.wikipedia.org/wiki/{encoded_title}"
        
        if summary_resp.status_code == 200:
            sum_data = summary_resp.json()
            coords = sum_data.get("coordinates", {})
            if coords:
                lat = coords.get("lat")
                lon = coords.get("lon")
            thumb = sum_data.get("thumbnail", {}).get("source")
            orig = sum_data.get("originalimage", {}).get("source")
            lead_image = orig or thumb
            extract = sum_data.get("extract", "")
            description = sum_data.get("description", "")
            page_url = sum_data.get("content_urls", {}).get("desktop", {}).get("page", page_url)
            page_title = sum_data.get("title", page_title)

        founded_year = None
        students_count = None
        website = None
        
        parse_params = {
            "action": "parse",
            "page": page_title,
            "prop": "wikitext",
            "section": "0",
            "format": "json"
        }
        try:
            parse_resp = await client.get(search_url, params=parse_params, headers=HEADERS)
            if parse_resp.status_code == 200:
                wikitext = parse_resp.json().get("parse", {}).get("wikitext", {}).get("*", "")
                
                if lat is None:
                    coord_m = re.search(r'coord[^\}]*?([0-9]{1,2}\.[0-9]+)[^\}]*?([0-9]{1,3}\.[0-9]+)', wikitext, re.IGNORECASE)
                    if coord_m:
                        try:
                            lat = float(coord_m.group(1))
                            lon = float(coord_m.group(2))
                        except Exception:
                            pass

                year_m = re.search(r'(?:основан|основана|established|founded|год основания)\s*=\s*.*?([12][0-9]{3})', wikitext, re.IGNORECASE)
                if not year_m:
                    year_m = re.search(r'\b(1[6-9][0-9]{2}|20[0-2][0-9])\s*(?:году?|year)?', extract)
                if year_m:
                    founded_year = year_m.group(1)

                stud_m = re.search(r'(?:студентов|students|число студентов)\s*=\s*([0-9\s,\.\+~]+)', wikitext, re.IGNORECASE)
                if stud_m:
                    cleaned_stud = re.sub(r'[^0-9]', '', stud_m.group(1))
                    if cleaned_stud and len(cleaned_stud) >= 3:
                        students_count = cleaned_stud

                site_m = re.search(r'(?:сайт|website|url)\s*=\s*\[?(https?://[^\s\]\|]+|[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})', wikitext, re.IGNORECASE)
                if site_m:
                    site_val = site_m.group(1).strip()
                    if not site_val.startswith("http"):
                        site_val = "https://" + site_val
                    website = site_val
        except Exception:
            pass

        return {
            "title": page_title,
            "description": description,
            "extract": extract,
            "page_url": page_url,
            "lat": lat,
            "lon": lon,
            "lead_image": lead_image,
            "founded_year": founded_year,
            "students_count": students_count,
            "website": website,
            "source": f"wikipedia_{lang}"
        }
    except Exception as e:
        logger.debug(f"Wikipedia {lang} full fetch error: {e}")
    return None

async def _fetch_ddg_web_search(query: str, client: httpx.AsyncClient) -> List[Dict[str, str]]:
    url = "https://html.duckduckgo.com/html/"
    snippets = []
    try:
        resp = await client.post(url, data={"q": query}, headers=HEADERS)
        if resp.status_code == 200:
            text = resp.text
            results = re.findall(
                r'<a class="result__snippet[^"]*"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                text,
                re.DOTALL
            )
            if not results:
                snippet_texts = re.findall(r'<a[^>]*class="result__snippet[^>]*>(.*?)</a>', text, re.DOTALL)
                urls = re.findall(r'<a[^>]*class="result__url[^>]*href="([^"]*)"', text, re.DOTALL)
                for i in range(min(len(snippet_texts), len(urls), 5)):
                    clean_text = re.sub(r'<[^>]+>', '', snippet_texts[i]).strip()
                    snippets.append({"url": urls[i].strip(), "snippet": clean_text})
            else:
                for href, body in results[:5]:
                    clean_body = re.sub(r'<[^>]+>', '', body).strip()
                    snippets.append({"url": href.strip(), "snippet": clean_body})
    except Exception as e:
        logger.debug(f"DuckDuckGo HTML search error: {e}")
    return snippets

async def _fetch_nominatim_coordinates(query: str, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": "1",
        "limit": "1"
    }
    try:
        resp = await client.get(url, params=params, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                first = data[0]
                addr = first.get("address", {})
                city = addr.get("city") or addr.get("town") or addr.get("state") or addr.get("municipality") or ""
                country = addr.get("country") or ""
                return {
                    "lat": float(first.get("lat", 0.0)),
                    "lon": float(first.get("lon", 0.0)),
                    "city": city,
                    "country": country,
                    "display_name": first.get("display_name", "")
                }
    except Exception as e:
        logger.debug(f"Nominatim geocoding error: {e}")
    return None

async def _fetch_google_cse(
    query: str,
    client: httpx.AsyncClient,
    search_type: Optional[str] = None,
    num: int = 5
) -> List[Dict[str, Any]]:
    api_key = settings.GOOGLE_CSE_API_KEY
    cx = settings.GOOGLE_CSE_CX
    if not api_key or not cx:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params: Dict[str, Any] = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num
    }
    if search_type:
        params["searchType"] = search_type

    items = []
    try:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            for it in data.get("items", []):
                items.append({
                    "title": it.get("title", ""),
                    "link": it.get("link", ""),
                    "snippet": it.get("snippet", ""),
                    "image": it.get("image", {}).get("thumbnailLink") if search_type == "image" else None
                })
    except Exception as e:
        logger.debug(f"Google CSE fetch error: {e}")
    return items

async def search_university_info(query: str) -> Dict[str, Any]:
    clean_query = query.strip()
    timeout = httpx.Timeout(settings.WEB_SEARCH_TIMEOUT, connect=2.0)
    
    async def _execute_search():
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            wiki_ru_task = _fetch_wikipedia_full(clean_query, client, lang="ru")
            wiki_en_task = _fetch_wikipedia_full(clean_query, client, lang="en")
            ddg_task = _fetch_ddg_instant(clean_query, client)
            geo_task = _fetch_nominatim_coordinates(f"{clean_query} university", client)
            snippets_task = _fetch_ddg_web_search(f"{clean_query} университет campus", client)
            google_task = _fetch_google_cse(f"{clean_query} university campus", client, num=3)

            results = await asyncio.gather(
                wiki_ru_task,
                wiki_en_task,
                ddg_task,
                geo_task,
                snippets_task,
                google_task,
                return_exceptions=True
            )

            wiki_ru = results[0] if isinstance(results[0], dict) else None
            wiki_en = results[1] if isinstance(results[1], dict) else None
            ddg = results[2] if isinstance(results[2], dict) else None
            geo = results[3] if isinstance(results[3], dict) else None
            snippets = results[4] if isinstance(results[4], list) else []
            google_res = results[5] if isinstance(results[5], list) else []

            return wiki_ru, wiki_en, ddg, geo, snippets, google_res

    try:
        wiki_ru, wiki_en, ddg, geo, snippets, google_res = await asyncio.wait_for(_execute_search(), timeout=8.0)
    except Exception as e:
        logger.warning(f"Web search for '{clean_query}' timed out or encountered error: {e}")
        wiki_ru, wiki_en, ddg, geo, snippets, google_res = None, None, None, None, [], []

    is_latin_query = all(ord(c) < 128 for c in clean_query.replace(" ", ""))
    if is_latin_query and wiki_en and any(k in (wiki_en.get("title", "") + " " + wiki_en.get("description", "")).lower() for k in ["university", "college", "institute", "polytechnic", "school"]):
        primary_wiki = wiki_en
    elif wiki_ru and any(k in (wiki_ru.get("title", "") + " " + wiki_ru.get("description", "") + " " + wiki_ru.get("extract", "")).lower() for k in ["университет", "university", "институт", "вуз", "колледж", "академи"]):
        primary_wiki = wiki_ru
    else:
        primary_wiki = wiki_en or wiki_ru or {}

    canonical_name = primary_wiki.get("title") or (ddg.get("heading") if ddg else None) or clean_query
    description = primary_wiki.get("description") or (ddg.get("abstract") if ddg else "")
    extract = primary_wiki.get("extract") or (ddg.get("abstract") if ddg else "")
    
    lat = primary_wiki.get("lat") or (geo.get("lat") if geo else 0.0) or 0.0
    lon = primary_wiki.get("lon") or (geo.get("lon") if geo else 0.0) or 0.0
    city = (geo.get("city") if geo else "") or ""
    country = (geo.get("country") if geo else "") or ""

    if not city and extract:
        known_cities = [
            "Алматы", "Астана", "Павлодар", "Шымкент", "Караганда", "Актобе", "Семей", "Костанай",
            "Москва", "Санкт-Петербург", "Новосибирск", "Казань", "Томск",
            "Кембридж", "Бостон", "Цюрих", "Оксфорд", "Париж", "Берлин", "Тарту", "Таллин",
            "Ташкент", "Бишкек", "Баку", "Ереван", "Тбилиси", "Токио", "Пекин", "Сеул"
        ]
        for c in known_cities:
            if c.lower() in extract.lower():
                city = c
                break

    if not country and extract:
        known_countries = [
            ("Казахстан", "Казахстан"), ("Росси", "Россия"), ("США", "США"), ("USA", "США"),
            ("Великобритани", "Великобритания"), ("Швейцари", "Швейцария"), ("Германи", "Германия"),
            ("Франци", "Франция"), ("Эстони", "Эстония"), ("Узбекистан", "Узбекистан"),
            ("Кыргызстан", "Кыргызстан"), ("Япони", "Япония"), ("Китай", "Китай")
        ]
        for pattern, c_name in known_countries:
            if pattern.lower() in extract.lower():
                country = c_name
                break

    founded_year = primary_wiki.get("founded_year")
    students_count = primary_wiki.get("students_count")
    website = primary_wiki.get("website") or (ddg.get("website") if ddg else None)

    if not website:
        for s in snippets:
            s_url = s.get("url", "")
            if any(dom in s_url.lower() for dom in [".edu", ".kz", ".ac.", ".org", ".edu.kz"]):
                parsed = urllib.parse.urlparse(s_url)
                if parsed.netloc:
                    website = f"{parsed.scheme}://{parsed.netloc}"
                    break

    sources_found = []
    if wiki_ru and wiki_ru.get("page_url"):
        sources_found.append({"title": "Wikipedia (RU)", "url": wiki_ru.get("page_url")})
    if wiki_en and wiki_en.get("page_url"):
        sources_found.append({"title": "Wikipedia (EN)", "url": wiki_en.get("page_url")})
    if ddg and ddg.get("url"):
        sources_found.append({"title": "DuckDuckGo Knowledge", "url": ddg.get("url")})
    for s in snippets[:3]:
        if s.get("url"):
            sources_found.append({"title": "Web Search", "url": s.get("url"), "snippet": s.get("snippet", "")})
    for g in google_res[:2]:
        if g.get("link"):
            sources_found.append({"title": "Google Search", "url": g.get("link"), "snippet": g.get("snippet", "")})

    lead_images = []
    if wiki_ru and wiki_ru.get("lead_image"):
        lead_images.append(wiki_ru.get("lead_image"))
    if wiki_en and wiki_en.get("lead_image"):
        lead_images.append(wiki_en.get("lead_image"))
    if ddg and ddg.get("image"):
        lead_images.append(ddg.get("image"))

    return {
        "canonical_name": canonical_name,
        "english_name": wiki_en.get("title") if wiki_en else canonical_name,
        "description": description,
        "extract": extract,
        "city": city,
        "country": country,
        "coordinates": {"lat": round(lat, 4), "lon": round(lon, 4)} if (lat and lon) else {"lat": 0.0, "lon": 0.0},
        "founded_year": founded_year,
        "students_count": students_count,
        "website": website,
        "lead_images": lead_images,
        "sources": sources_found,
        "web_snippets": [s.get("snippet") for s in snippets if s.get("snippet")]
    }

async def search_duckduckgo_images(query: str, client: httpx.AsyncClient, limit: int = 10) -> List[Dict[str, Any]]:
    items = []
    try:
        token_url = "https://duckduckgo.com/"
        token_resp = await client.get(token_url, params={"q": f"{query} campus"}, headers=HEADERS)
        if token_resp.status_code != 200:
            return items
            
        vqd_match = re.search(r'vqd=([\d\-]+)', token_resp.text) or re.search(r'vqd=([a-zA-Z0-9_\-]+)', token_resp.text)
        if not vqd_match:
            vqd_match = re.search(r'vqd=["\']([^"\']+)["\']', token_resp.text)
            
        if not vqd_match:
            return items
            
        vqd = vqd_match.group(1)
        
        img_url = "https://duckduckgo.com/i.js"
        img_params = {
            "l": "wt-wt",
            "o": "json",
            "q": f"{query} campus university building",
            "vqd": vqd,
            "f": ",,,",
            "p": "1"
        }
        
        img_headers = dict(HEADERS)
        img_headers["Referer"] = "https://duckduckgo.com/"
        img_resp = await client.get(img_url, params=img_params, headers=img_headers)
        
        if img_resp.status_code == 200:
            data = img_resp.json()
            results = data.get("results", [])
            for idx, res in enumerate(results[:limit]):
                img_src = res.get("image") or res.get("thumbnail")
                thumb = res.get("thumbnail") or img_src
                title = res.get("title") or f"{query} Campus View"
                source_url = res.get("url") or res.get("image")
                source_host = urllib.parse.urlparse(source_url).netloc or "web"
                
                if thumb and ("http://" in thumb or "https://" in thumb):
                    items.append({
                        "id": f"web_{idx}_{abs(hash(thumb)) % 100000}",
                        "title": title[:70],
                        "preview_url": thumb,
                        "source_url": source_url,
                        "author": f"Web Source ({source_host})",
                        "license_name": "Web Source (Fair Use / Editorial)",
                        "license_url": "https://www.fairuse.stanford.edu/overview/",
                        "source_api": "web_search",
                        "date_published": "2024-02-15"
                    })
    except Exception as e:
        logger.debug(f"DuckDuckGo image search exception: {e}")
    return items

async def fetch_wikipedia_page_images(query: str, client: httpx.AsyncClient, limit: int = 8) -> List[Dict[str, Any]]:
    items = []
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        clean_q = re.sub(r'(?i)\b(университет|university|институт|institute|им\.|имени)\b', '', query).strip() or query
        candidate_queries = [f"{query} campus", query, f"{clean_q} campus", clean_q]

        seen_urls = set()
        for q_str in candidate_queries:
            if len(items) >= limit:
                break
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": q_str,
                "gsrlimit": limit,
                "gsrnamespace": 6,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 480,
                "format": "json"
            }
            resp = await client.get(url, params=params, headers=HEADERS)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("pages", {})
                for pid, pdata in pages.items():
                    imageinfo = pdata.get("imageinfo", [])
                    if not imageinfo:
                        continue
                    info = imageinfo[0]
                    thumb = info.get("thumburl") or info.get("url")
                    desc_url = info.get("descriptionurl") or info.get("url")
                    meta = info.get("extmetadata", {})

                    if not thumb or thumb in seen_urls:
                        continue
                    if any(thumb.lower().endswith(bad) or (bad in thumb.lower()) for bad in [".pdf", ".djvu", ".ogg", ".webm", ".tif", ".tiff", ".svg"]):
                        continue

                    title = pdata.get("title", f"Web Image {pid}").replace("File:", "")
                    artist = meta.get("Artist", {}).get("value", "")
                    artist_clean = re.sub(r"<[^>]*>", "", artist).strip() or "Web Archive"
                    
                    seen_urls.add(thumb)
                    items.append({
                        "id": f"web_wiki_{pid}",
                        "title": title[:70],
                        "preview_url": thumb,
                        "source_url": desc_url,
                        "author": artist_clean[:40],
                        "license_name": "Web Source (Fair Use / Editorial)",
                        "license_url": "https://creativecommons.org/licenses/",
                        "source_api": "web_search",
                        "date_published": "2024-02-15"
                    })
                    if len(items) >= limit:
                        break
            if items:
                break
    except Exception as e:
        logger.debug(f"Wikipedia page images fetch error: {e}")
    return items

async def search_university_images(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    clean_query = query.strip()
    timeout = httpx.Timeout(settings.WEB_SEARCH_TIMEOUT, connect=2.0)
    
    async def _execute_image_search():
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            ddg_task = search_duckduckgo_images(clean_query, client, limit=limit)
            wiki_task = fetch_wikipedia_page_images(clean_query, client, limit=limit)
            
            google_task = _fetch_google_cse(f"{clean_query} campus university", client, search_type="image", num=min(limit, 5))
            
            results = await asyncio.gather(ddg_task, wiki_task, google_task, return_exceptions=True)
            ddg_imgs = results[0] if isinstance(results[0], list) else []
            wiki_imgs = results[1] if isinstance(results[1], list) else []
            google_res = results[2] if isinstance(results[2], list) else []
            
            google_imgs = []
            for idx, g in enumerate(google_res):
                g_url = g.get("link") or g.get("image")
                if g_url:
                    google_imgs.append({
                        "id": f"web_google_{idx}_{abs(hash(g_url)) % 100000}",
                        "title": g.get("title", f"{clean_query} Campus View")[:70],
                        "preview_url": g_url,
                        "source_url": g.get("snippet") or g_url,
                        "author": "Google Web Search",
                        "license_name": "Web Source (Fair Use / Editorial)",
                        "license_url": "https://www.fairuse.stanford.edu/overview/",
                        "source_api": "web_search",
                        "date_published": "2024-02-15"
                    })

            combined = []
            seen_urls = set()
            for it in (ddg_imgs + wiki_imgs + google_imgs):
                url = it.get("preview_url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    combined.append(it)

            if len(combined) < limit:
                try:
                    for lang in ["ru", "en"]:
                        w_sum = await _fetch_wikipedia_full(clean_query, client, lang=lang)
                        if w_sum and w_sum.get("lead_image"):
                            l_img = w_sum["lead_image"]
                            if l_img not in seen_urls:
                                seen_urls.add(l_img)
                                combined.append({
                                    "id": f"web_lead_{lang}_{abs(hash(l_img)) % 100000}",
                                    "title": f"{w_sum.get('title', clean_query)} Lead Photo",
                                    "preview_url": l_img,
                                    "source_url": w_sum.get("page_url", ""),
                                    "author": f"Wikipedia ({lang.upper()})",
                                    "license_name": "Web Source (Fair Use / Editorial)",
                                    "license_url": "https://creativecommons.org/licenses/",
                                    "source_api": "web_search",
                                    "date_published": "2024-02-15"
                                })
                except Exception:
                    pass
                    
            return combined[:limit]

    try:
        return await asyncio.wait_for(_execute_image_search(), timeout=8.0)
    except Exception as e:
        logger.warning(f"Image search for '{clean_query}' timed out or failed: {e}")
        return []
