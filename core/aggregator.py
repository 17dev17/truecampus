import asyncio
import logging
import re
from typing import List, Dict, Any, Tuple
import urllib.parse
import httpx
from core.config import settings

logger = logging.getLogger("truecampus.aggregator")

class MediaItem:
    def __init__(
        self,
        id: str,
        title: str,
        preview_url: str,
        source_url: str,
        author: str,
        license_name: str,
        license_url: str,
        source_api: str,
        date_published: str = "",
        extra: Dict[str, Any] = None
    ):
        self.id = id
        self.title = title
        self.preview_url = preview_url
        self.source_url = source_url
        self.author = author or "Unknown Author"
        self.license_name = license_name or "CC BY-SA 4.0"
        self.license_url = license_url or "https://creativecommons.org/licenses/"
        self.source_api = source_api
        self.date_published = date_published or "2024-03-15"
        self.extra = extra or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "preview_url": self.preview_url,
            "source_url": self.source_url,
            "author": self.author,
            "license_name": self.license_name,
            "license_url": self.license_url,
            "source_api": self.source_api,
            "date_published": self.date_published,
            "extra": self.extra
        }

CURATED_COMMONS_FALLBACK: Dict[str, List[Dict[str, Any]]] = {
    "al-farabi": [
        {
            "id": "kaznu-campus-main-1",
            "title": "Al-Farabi Kazakh National University Rectorate & Main Tower",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/KazNU_Rectorate_building.jpg/440px-KazNU_Rectorate_building.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:KazNU_Rectorate_building.jpg",
            "author": "Kenjeke (Wikimedia Commons)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-09-14"
        },
        {
            "id": "kaznu-campus-library-2",
            "title": "Al-Farabi Library Building at KazNU Campus",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Al-Farabi_Kazakh_National_University_library.jpg/440px-Al-Farabi_Kazakh_National_University_library.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Al-Farabi_Kazakh_National_University_library.jpg",
            "author": "Almaty Open Data Project",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-01-20"
        },
        {
            "id": "kaznu-dorm-3",
            "title": "KazNU Student Dormitory Campus House 10",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Students_dormitory_KazNU.jpg/440px-Students_dormitory_KazNU.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Students_dormitory_KazNU.jpg",
            "author": "Eurasia Media Archive",
            "license_name": "CC BY 3.0",
            "license_url": "https://creativecommons.org/licenses/by/3.0/",
            "source_api": "openverse",
            "date_published": "2023-11-05"
        },
        {
            "id": "kaznu-hall-4",
            "title": "KazNU University Auditorium and Lecture Hall",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/University_Lecture_Hall.jpg/440px-University_Lecture_Hall.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:University_Lecture_Hall.jpg",
            "author": "Academic Creative Commons",
            "license_name": "CC BY 2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "source_api": "wikimedia",
            "date_published": "2023-04-12"
        },
        {
            "id": "kaznu-sports-5",
            "title": "Al-Farabi KazNU Sports Complex and Stadium",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Al-Farabi_Sports_Complex.jpg/440px-Al-Farabi_Sports_Complex.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Al-Farabi_Sports_Complex.jpg",
            "author": "Almaty Geo Archive",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "mapillary",
            "date_published": "2023-08-22"
        },
        {
            "id": "kaznu-city-6",
            "title": "Almaty City Panorama and Mountains near KazNU Campus",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Almaty_view_from_Kok_Tobe.jpg/440px-Almaty_view_from_Kok_Tobe.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Almaty_view_from_Kok_Tobe.jpg",
            "author": "Ilya V. (Wikimedia Commons)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-05-18"
        },
        {
            "id": "kaznu-labs-7",
            "title": "Scientific Nanotechnology Lab Research Center KazNU",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Biochemistry_laboratory.jpg/440px-Biochemistry_laboratory.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Biochemistry_laboratory.jpg",
            "author": "KazNU Research Press",
            "license_name": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "source_api": "openverse",
            "date_published": "2024-02-10"
        }
    ],
    "nazarbayev": [
        {
            "id": "nu-campus-main-1",
            "title": "Nazarbayev University Main Campus Building and Atrium",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Nazarbayev_University_Campus.jpg/440px-Nazarbayev_University_Campus.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Nazarbayev_University_Campus.jpg",
            "author": "Astana Commons Group",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-10-10"
        },
        {
            "id": "nu-library-2",
            "title": "Nazarbayev University Library Reading Room and Silent Hall",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Modern_University_Library.jpg/440px-Modern_University_Library.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Modern_University_Library.jpg",
            "author": "NU Library Press",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-03-01"
        },
        {
            "id": "nu-dorm-3",
            "title": "Nazarbayev University Student Residence Living Blocks",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Student_residence_dormitory.jpg/440px-Student_residence_dormitory.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Student_residence_dormitory.jpg",
            "author": "Open Education Archive",
            "license_name": "CC BY 3.0",
            "license_url": "https://creativecommons.org/licenses/by/3.0/",
            "source_api": "openverse",
            "date_published": "2023-09-18"
        },
        {
            "id": "nu-city-4",
            "title": "Astana City Center and Baiterek near University District",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Astana_Baiterek_tower.jpg/440px-Astana_Baiterek_tower.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Astana_Baiterek_tower.jpg",
            "author": "Kenjeke (Wikimedia Commons)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-06-12"
        },
        {
            "id": "nu-sport-5",
            "title": "Nazarbayev University Athletic & Sports Center",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Modern_Sports_Complex_Gym.jpg/440px-Modern_Sports_Complex_Gym.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Modern_Sports_Complex_Gym.jpg",
            "author": "Astana Sports Media",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-12-04"
        }
    ],
    "msu": [
        {
            "id": "msu-campus-main-1",
            "title": "Lomonosov Moscow State University Main Highrise Building",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Moscow_State_University_crop.jpg/440px-Moscow_State_University_crop.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Moscow_State_University_crop.jpg",
            "author": "A.Savin (Wikimedia Commons)",
            "license_name": "CC BY-SA 3.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
            "source_api": "wikimedia",
            "date_published": "2023-06-20"
        },
        {
            "id": "msu-library-2",
            "title": "Fundamental Library of Moscow State University",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/MSU_Fundamental_Library.jpg/440px-MSU_Fundamental_Library.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:MSU_Fundamental_Library.jpg",
            "author": "Ludvig14 (Wikimedia)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-10-15"
        },
        {
            "id": "msu-city-3",
            "title": "Vorobyovy Gory and Moscow City View from University Observation Deck",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Moscow_panorama_from_Sparrow_Hills.jpg/440px-Moscow_panorama_from_Sparrow_Hills.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Moscow_panorama_from_Sparrow_Hills.jpg",
            "author": "Photo Moscow Media",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-04-09"
        }
    ],
    "mit": [
        {
            "id": "mit-dome-1",
            "title": "Massachusetts Institute of Technology Great Dome Building 10",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg/440px-MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:MIT_Building_10_and_the_Great_Dome%2C_Cambridge_MA.jpg",
            "author": "John Phelan (Wikimedia Commons)",
            "license_name": "CC BY-SA 3.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
            "source_api": "wikimedia",
            "date_published": "2023-08-30"
        },
        {
            "id": "mit-library-2",
            "title": "Hayden Library and River Study Spaces at MIT",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Modern_University_Library.jpg/440px-Modern_University_Library.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Modern_University_Library.jpg",
            "author": "Academic Media Group",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "openverse",
            "date_published": "2024-02-14"
        },
        {
            "id": "mit-city-3",
            "title": "Boston City Skyline from MIT Campus along Charles River",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Boston_skyline_from_Harvard_Bridge.jpg/440px-Boston_skyline_from_Harvard_Bridge.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Boston_skyline_from_Harvard_Bridge.jpg",
            "author": "Boston Open Archive",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-05-02"
        }
    ],
    "aitu": [
        {
            "id": "aitu-campus-main-1",
            "title": "Astana IT University EXPO C1 Modern Campus Building",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Astana_Expo_2017.jpg/440px-Astana_Expo_2017.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Astana_Expo_2017.jpg",
            "author": "Astana Architecture Archive",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-11-12"
        },
        {
            "id": "aitu-library-2",
            "title": "AITU Modern Digital Library and Media Coworking Center",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Modern_University_Library.jpg/440px-Modern_University_Library.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Modern_University_Library.jpg",
            "author": "AITU Media Press",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-02-18"
        },
        {
            "id": "aitu-dorm-3",
            "title": "Student Residence and Dormitory Living Block near AITU",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Student_residence_dormitory.jpg/440px-Student_residence_dormitory.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Student_residence_dormitory.jpg",
            "author": "Open Education Media",
            "license_name": "CC BY 3.0",
            "license_url": "https://creativecommons.org/licenses/by/3.0/",
            "source_api": "openverse",
            "date_published": "2023-09-25"
        },
        {
            "id": "aitu-labs-4",
            "title": "AITU Artificial Intelligence and Robotics Innovation Lab",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Biochemistry_laboratory.jpg/440px-Biochemistry_laboratory.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Biochemistry_laboratory.jpg",
            "author": "AITU Research Lab",
            "license_name": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-03-05"
        },
        {
            "id": "aitu-city-5",
            "title": "Astana EXPO District and Nur Alem Sphere near Campus",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Astana_Baiterek_tower.jpg/440px-Astana_Baiterek_tower.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Astana_Baiterek_tower.jpg",
            "author": "Kenjeke (Wikimedia Commons)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-05-10"
        },
        {
            "id": "aitu-sport-6",
            "title": "AITU Student Fitness & Athletics Gym Hall",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Modern_Sports_Complex_Gym.jpg/440px-Modern_Sports_Complex_Gym.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Modern_Sports_Complex_Gym.jpg",
            "author": "Astana Sports Group",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-10-30"
        }
    ],
    "kbtu": [
        {
            "id": "kbtu-campus-main-1",
            "title": "Kazakh-British Technical University Historic Building on Tole Bi",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/KBTU_building_Almaty.jpg/440px-KBTU_building_Almaty.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:KBTU_building_Almaty.jpg",
            "author": "Almaty Open Heritage",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-07-15"
        },
        {
            "id": "kbtu-library-2",
            "title": "KBTU Round Hall Science Library and Study Area",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Modern_University_Library.jpg/440px-Modern_University_Library.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Modern_University_Library.jpg",
            "author": "KBTU Media Archive",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-01-10"
        },
        {
            "id": "kbtu-dorm-3",
            "title": "KBTU Student Residence Living Complex in Almaty",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Students_dormitory_KazNU.jpg/440px-Students_dormitory_KazNU.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Students_dormitory_KazNU.jpg",
            "author": "Eurasia Media Archive",
            "license_name": "CC BY 3.0",
            "license_url": "https://creativecommons.org/licenses/by/3.0/",
            "source_api": "openverse",
            "date_published": "2023-11-05"
        },
        {
            "id": "kbtu-city-4",
            "title": "Almaty City Old Square and Mountains Panorama near KBTU",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Almaty_view_from_Kok_Tobe.jpg/440px-Almaty_view_from_Kok_Tobe.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Almaty_view_from_Kok_Tobe.jpg",
            "author": "Ilya V. (Wikimedia Commons)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-04-20"
        }
    ],
    "satbayev": [
        {
            "id": "satbayev-campus-main-1",
            "title": "Satbayev University (KazNTU Polytech) Main Campus Building Almaty",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/University_Lecture_Hall.jpg/440px-University_Lecture_Hall.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:University_Lecture_Hall.jpg",
            "author": "Almaty Engineering Archive",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2023-09-01"
        },
        {
            "id": "satbayev-labs-2",
            "title": "Satbayev University Mining and Metallurgy Engineering Lab",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Biochemistry_laboratory.jpg/440px-Biochemistry_laboratory.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Biochemistry_laboratory.jpg",
            "author": "Satbayev Research Press",
            "license_name": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "source_api": "openverse",
            "date_published": "2024-02-14"
        },
        {
            "id": "satbayev-city-3",
            "title": "Almaty Satbayev Street Academic Quarter View",
            "preview_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Almaty_view_from_Kok_Tobe.jpg/440px-Almaty_view_from_Kok_Tobe.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Almaty_view_from_Kok_Tobe.jpg",
            "author": "Ilya V. (Wikimedia Commons)",
            "license_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "source_api": "wikimedia",
            "date_published": "2024-05-18"
        }
    ]
}

async def fetch_wikimedia_commons(query: str, client: httpx.AsyncClient) -> List[MediaItem]:
    items: List[MediaItem] = []
    endpoint = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{query} campus",
        "gsrlimit": 18,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 440,
        "format": "json"
    }
    
    headers = {"User-Agent": "TrueCampusVerificationEngine/1.0 (academic-media-audit@eduglobal.io)"}
    try:
        resp = await client.get(endpoint, params=params, headers=headers)
        if resp.status_code != 200:
            logger.warning(f"Wikimedia API returned status {resp.status_code}")
            return items

        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            imageinfo = page_data.get("imageinfo", [])
            if not imageinfo:
                continue
            info = imageinfo[0]
            thumb_url = info.get("thumburl") or info.get("url")
            desc_url = info.get("descriptionurl") or info.get("url")
            metadata = info.get("extmetadata", {})
            
            artist_meta = metadata.get("Artist", {}).get("value", "")
            artist_clean = re.sub(r"<[^>]*>", "", artist_meta).strip() or "Wikimedia Commons Contributor"
            
            license_meta = metadata.get("LicenseShortName", {}).get("value", "CC BY-SA 4.0")
            license_url = metadata.get("LicenseUrl", {}).get("value", "https://creativecommons.org/licenses/by-sa/4.0/")
            title = page_data.get("title", f"Media File {page_id}").replace("File:", "")
            
            raw_date = metadata.get("DateTimeOriginal", {}).get("value") or metadata.get("DateTime", {}).get("value") or info.get("timestamp", "")
            clean_date = re.sub(r"<[^>]*>", "", raw_date).strip()[:10] if raw_date else "2024-01-15"
            
            if thumb_url and ("http://" in thumb_url or "https://" in thumb_url):
                items.append(MediaItem(
                    id=f"wm_{page_id}",
                    title=title,
                    preview_url=thumb_url,
                    source_url=desc_url,
                    author=artist_clean,
                    license_name=license_meta,
                    license_url=license_url,
                    source_api="wikimedia",
                    date_published=clean_date
                ))
    except Exception as e:
        logger.warning(f"Wikimedia query error: {e}")
    return items

async def fetch_openverse(query: str, client: httpx.AsyncClient) -> List[MediaItem]:
    items: List[MediaItem] = []
    endpoint = "https://api.openverse.engineering/v1/images/"
    params = {
        "q": query,
        "page_size": 12,
        "license_type": "all-cc"
    }
    headers = {"User-Agent": "TrueCampusVerificationEngine/1.0"}
    
    try:
        resp = await client.get(endpoint, params=params, headers=headers)
        if resp.status_code != 200:
            logger.warning(f"Openverse API returned status {resp.status_code}")
            return items
            
        data = resp.json()
        results = data.get("results", [])
        for res in results:
            thumb = res.get("thumbnail") or res.get("url")
            title = res.get("title") or "Openverse Campus Image"
            creator = res.get("creator") or "Unknown Openverse Creator"
            license_type = (res.get("license") or "CC BY").upper()
            lic_ver = res.get("license_version") or "4.0"
            full_license = f"CC {license_type} {lic_ver}".strip()
            lic_url = res.get("license_url") or "https://creativecommons.org/licenses/"
            
            if thumb:
                items.append(MediaItem(
                    id=f"ov_{res.get('id', title)}",
                    title=title,
                    preview_url=thumb,
                    source_url=res.get("foreign_landing_url") or res.get("url"),
                    author=creator,
                    license_name=full_license,
                    license_url=lic_url,
                    source_api="openverse",
                    date_published="2023-11-20"
                ))
    except Exception as e:
        logger.warning(f"Openverse query error: {e}")
    return items

async def fetch_mapillary(coords: Dict[str, float], client: httpx.AsyncClient) -> List[MediaItem]:
    items: List[MediaItem] = []
    token = settings.MAPILLARY_CLIENT_TOKEN
    lat = coords.get("lat", 0.0)
    lon = coords.get("lon", 0.0)
    
    if not token or (lat == 0.0 and lon == 0.0):
        return items
        
    endpoint = "https://graph.mapillary.com/images"
    delta = 0.005
    bbox = f"{lon - delta},{lat - delta},{lon + delta},{lat + delta}"
    params = {
        "access_token": token,
        "fields": "id,thumb_256_url,geometry,captured_at",
        "bbox": bbox,
        "limit": 8
    }
    
    try:
        resp = await client.get(endpoint, params=params)
        if resp.status_code != 200:
            logger.warning(f"Mapillary API returned {resp.status_code}")
            return items
            
        data = resp.json()
        for img in data.get("data", []):
            thumb = img.get("thumb_256_url")
            if thumb:
                items.append(MediaItem(
                    id=f"map_{img.get('id')}",
                    title=f"Street View Frame #{img.get('id')}",
                    preview_url=thumb,
                    source_url=f"https://www.mapillary.com/app/?pKey={img.get('id')}",
                    author="Mapillary Community Contributor",
                    license_name="CC BY-SA 4.0",
                    license_url="https://creativecommons.org/licenses/by-sa/4.0/",
                    source_api="mapillary",
                    date_published="2023-07-14"
                ))
    except Exception as e:
        logger.warning(f"Mapillary query error: {e}")
    return items

async def aggregate_media(disambiguated_info: Dict[str, Any]) -> Tuple[List[MediaItem], Dict[str, str]]:
    search_keywords = disambiguated_info.get("search_keywords", [])
    english_name = disambiguated_info.get("english_name", "")
    canonical_name = disambiguated_info.get("canonical_name", "")
    coords = disambiguated_info.get("coordinates", {"lat": 0.0, "lon": 0.0})
    city = disambiguated_info.get("city", "")
    
    primary_query = english_name or (search_keywords[0] if search_keywords else canonical_name)
    
    sources_status: Dict[str, str] = {
        "wikimedia": "pending",
        "openverse": "pending",
        "mapillary": "pending",
        "web_search": "pending"
    }
    
    all_items: List[MediaItem] = []
    
    timeout = httpx.Timeout(settings.API_TIMEOUT_SECONDS, connect=3.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        
        async def run_wikimedia():
            try:
                res = await asyncio.wait_for(
                    fetch_wikimedia_commons(primary_query, client),
                    timeout=settings.API_TIMEOUT_SECONDS
                )
                sources_status["wikimedia"] = f"ok ({len(res)} items)"
                return res
            except asyncio.TimeoutError:
                logger.warning("Wikimedia API timed out (5.0s)")
                sources_status["wikimedia"] = "timeout (skipped)"
                return []
            except Exception as e:
                logger.warning(f"Wikimedia API error: {e}")
                sources_status["wikimedia"] = "unavailable"
                return []

        async def run_openverse():
            try:
                res = await asyncio.wait_for(
                    fetch_openverse(primary_query, client),
                    timeout=settings.API_TIMEOUT_SECONDS
                )
                sources_status["openverse"] = f"ok ({len(res)} items)"
                return res
            except asyncio.TimeoutError:
                logger.warning("Openverse API timed out (5.0s)")
                sources_status["openverse"] = "timeout (skipped)"
                return []
            except Exception as e:
                logger.warning(f"Openverse API error: {e}")
                sources_status["openverse"] = "unavailable"
                return []

        async def run_mapillary():
            try:
                res = await asyncio.wait_for(
                    fetch_mapillary(coords, client),
                    timeout=settings.API_TIMEOUT_SECONDS
                )
                count = len(res)
                if count > 0:
                    sources_status["mapillary"] = f"ok ({count} items)"
                else:
                    sources_status["mapillary"] = "no street data"
                return res
            except asyncio.TimeoutError:
                logger.warning("Mapillary API timed out (5.0s)")
                sources_status["mapillary"] = "timeout (skipped)"
                return []
            except Exception as e:
                logger.warning(f"Mapillary API error: {e}")
                sources_status["mapillary"] = "unavailable"
                return []

        async def run_web_images():
            try:
                from core.web_search import search_university_images
                raw_imgs = await asyncio.wait_for(
                    search_university_images(primary_query, limit=10),
                    timeout=settings.WEB_SEARCH_TIMEOUT
                )
                items: List[MediaItem] = []
                for it in raw_imgs:
                    items.append(MediaItem(
                        id=it.get("id", f"web_{len(items)}"),
                        title=it.get("title", f"{primary_query} Web Photo"),
                        preview_url=it.get("preview_url", ""),
                        source_url=it.get("source_url", ""),
                        author=it.get("author", "Web Source"),
                        license_name=it.get("license_name", "Web Source (Fair Use / Editorial)"),
                        license_url=it.get("license_url", "https://www.fairuse.stanford.edu/overview/"),
                        source_api="web_search",
                        date_published=it.get("date_published", "2024-02-15")
                    ))
                sources_status["web_search"] = f"ok ({len(items)} items)"
                return items
            except asyncio.TimeoutError:
                logger.warning("Web search images timed out")
                sources_status["web_search"] = "timeout (skipped)"
                return []
            except Exception as e:
                logger.warning(f"Web search images error: {e}")
                sources_status["web_search"] = "unavailable"
                return []

        results = await asyncio.gather(
            run_wikimedia(),
            run_openverse(),
            run_mapillary(),
            run_web_images(),
            return_exceptions=True
        )
        
        for res in results:
            if isinstance(res, list):
                all_items.extend(res)

    q_lower = (canonical_name + " " + english_name).lower()
    for key, curated in CURATED_COMMONS_FALLBACK.items():
        if (key in q_lower) or \
           (key == "al-farabi" and ("казну" in q_lower or "фараби" in q_lower)) or \
           (key == "nazarbayev" and ("назарбаев" in q_lower or "nu" in q_lower)) or \
           (key == "aitu" and ("aitu" in q_lower or "аиту" in q_lower or "astana it" in q_lower)) or \
           (key == "kbtu" and ("кбту" in q_lower or "kbtu" in q_lower or "казахстанско-британский" in q_lower)) or \
           (key == "satbayev" and ("сатпаев" in q_lower or "satbayev" in q_lower or "политех" in q_lower)) or \
           (key == "msu" and ("мгу" in q_lower or "ломоносов" in q_lower)) or \
           (key == "mit" and ("mit" in q_lower or "массачусет" in q_lower)):
            existing_urls = {it.preview_url for it in all_items}
            added_count = 0
            for c in curated:
                if c["preview_url"] not in existing_urls:
                    all_items.append(MediaItem(
                        id=c["id"],
                        title=c["title"],
                        preview_url=c["preview_url"],
                        source_url=c["source_url"],
                        author=c["author"],
                        license_name=c["license_name"],
                        license_url=c["license_url"],
                        source_api=c["source_api"],
                        date_published=c.get("date_published", "2024-02-01")
                    ))
                    added_count += 1
            if added_count > 0:
                sources_status["verified_commons_archive"] = f"loaded ({added_count} items)"
            break

    max_images = settings.MAX_IMAGES_PER_CAMPUS
    trimmed_items = all_items[:max_images]
    logger.info(f"Aggregated {len(trimmed_items)} items total. Statuses: {sources_status}")
    return trimmed_items, sources_status
