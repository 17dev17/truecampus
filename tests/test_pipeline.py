# -*- coding: utf-8 -*-
import os
import sys
import unittest
import asyncio
from PIL import Image, ImageDraw

# Ensure truecampus path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.disambiguator import disambiguate_university, detect_ambiguity
from core.processor import deduplicate_with_phash, calculate_trust_score, CATEGORIES
from core.rules import apply_rule_engine, verify_legal_purity
from core.summary import _generate_rule_based_summary
from core.pdf_generator import build_pdf_report
from core.campus_data import get_campus_extended_data, calculate_haversine_distance

class TestTrueCampusPipeline(unittest.IsolatedAsyncioTestCase):

    async def test_01_disambiguation_and_ambiguity(self):
        """Test university disambiguation, typo detection, and ambiguous query resolution."""
        # 1. Test CIS university
        res1 = await disambiguate_university("КазНУ им. Аль-Фараби")
        self.assertIn("Казахский", res1["canonical_name"])
        self.assertEqual(res1["city"], "Алматы")
        self.assertEqual(res1["country"], "Казахстан")
        self.assertTrue(len(res1["search_keywords"]) > 0)

        # 2. Test Western university
        res2 = await disambiguate_university("MIT")
        self.assertIn("Массачусетский", res2["canonical_name"])
        self.assertIn("Massachusetts", res2["english_name"])
        self.assertEqual(res2["country_code"], "US")
        self.assertFalse(res2["has_typo"])

        # 3. Test AITU and KBTU (No false-positive typo banner)
        res_aitu = await disambiguate_university("Aitu University")
        self.assertIn("Astana IT", res_aitu["canonical_name"])
        self.assertFalse(res_aitu["has_typo"])

        res_kbtu = await disambiguate_university("КБТУ")
        self.assertIn("Казахстанско-Британский", res_kbtu["canonical_name"])
        self.assertFalse(res_kbtu["has_typo"])

        # 4. Test Typo Detection (Requirement 1)
        res_typo = await disambiguate_university("харвард")
        self.assertTrue(res_typo["has_typo"])
        self.assertIn("Гарвард", res_typo["did_you_mean"])

        res_koznu = await disambiguate_university("козну")
        self.assertTrue(res_koznu["has_typo"])
        self.assertIn("Фараби", res_koznu["did_you_mean"])

        # 5. Test Ambiguity Detection (Requirement 1)
        ambig = detect_ambiguity("Политех")
        self.assertIsNotNone(ambig)
        self.assertTrue(len(ambig) >= 2)
        self.assertTrue(any("Сатпаев" in c["canonical_name"] or "Satbayev" in c["canonical_name"] for c in ambig))

        res_ambig = await disambiguate_university("Политех")
        self.assertTrue(res_ambig["is_ambiguous"])
        self.assertTrue(len(res_ambig["candidates"]) >= 2)

    def test_02_phash_deduplication(self):
        """Test perceptual hashing and Hamming distance <= 6 duplicate dropping."""
        img1 = Image.new("RGB", (224, 224), color=(30, 30, 30))
        draw1 = ImageDraw.Draw(img1)
        draw1.rectangle([20, 20, 100, 100], fill=(255, 255, 255))
        draw1.line([0, 0, 224, 224], fill=(255, 0, 0), width=4)

        img2 = img1.copy()
        draw2 = ImageDraw.Draw(img2)
        draw2.point([1, 1], fill=(254, 254, 254))

        img3 = Image.new("RGB", (224, 224), color=(240, 240, 240))
        draw3 = ImageDraw.Draw(img3)
        for i in range(0, 224, 20):
            draw3.line([i, 0, i, 224], fill=(0, 0, 0), width=3)
            draw3.line([0, i, 224, i], fill=(0, 0, 255), width=3)

        items = [
            {"id": "img1", "title": "Original Photo", "_pil_image": img1},
            {"id": "img2", "title": "Duplicate Photo (slight variation)", "_pil_image": img2},
            {"id": "img3", "title": "Distinct Pattern Photo", "_pil_image": img3}
        ]

        unique, dropped = deduplicate_with_phash(items, threshold=6)
        self.assertEqual(len(unique), 2, "Should retain exactly 2 unique images")
        self.assertEqual(dropped, 1, "Should drop 1 near-duplicate image")
        self.assertEqual(unique[0]["id"], "img1")
        self.assertEqual(unique[1]["id"], "img3")

    def test_03_rule_engine_honest_uncertainty_and_categories(self):
        """Test rule engine across all 8 categories and 'Честная неопределенность' marking."""
        self.assertEqual(len(CATEGORIES), 8, "Must support all 8 categories from hackathon specification")
        self.assertIn("library", CATEGORIES)
        self.assertIn("city", CATEGORIES)
        self.assertIn("sport", CATEGORIES)
        self.assertIn("labs", CATEGORIES)
        self.assertIn("student_life", CATEGORIES)

        processed = [
            {
                "id": "c1",
                "category": "campus",
                "confidence": 0.88,
                "trust_score": 92,
                "license_name": "CC BY-SA 4.0",
                "source_url": "https://commons.wikimedia.org/wiki/File:Campus.jpg",
                "author": "Alice"
            },
            {
                "id": "c2",
                "category": "dormitory",
                "confidence": 0.52,  # Below 0.65 threshold!
                "trust_score": 55,
                "license_name": "CC BY 3.0",
                "source_url": "https://openverse.org/image/dorm.jpg",
                "author": "Bob"
            }
        ]

        result = apply_rule_engine(processed)
        cats = result["categories"]

        self.assertTrue(cats["campus"]["is_verified"])
        self.assertEqual(cats["campus"]["items_count"], 1)
        self.assertIn("Верифицировано", cats["campus"]["status_text"])

        # Dormitory category should trigger 'Честная неопределенность'
        self.assertFalse(cats["dormitory"]["is_verified"])
        self.assertEqual(cats["dormitory"]["items_count"], 0)
        self.assertEqual(cats["dormitory"]["status_text"], "Нет верифицированных данных")
        self.assertEqual(len(cats["dormitory"]["rejections"]), 1)

        # Honest uncertainty flag must be active because not all 8 categories are verified
        self.assertTrue(result["summary"]["honest_uncertainty_active"])

    def test_04_campus_extended_data_and_distance(self):
        """Test bonus features: distance to city center, transit times, climate, budget, reviews."""
        dist = calculate_haversine_distance(43.2241, 76.9247, 43.2567, 76.9286)
        self.assertTrue(3.0 <= dist <= 4.5, f"Almaty KazNU distance should be ~3.8km, got {dist}")

        ext = get_campus_extended_data(
            "Казахский национальный университет имени аль-Фараби",
            "Алматы",
            "Казахстан",
            {"lat": 43.2241, "lon": 76.9247}
        )

        self.assertIn("distance_km", ext)
        self.assertTrue(ext["distance_km"] > 0)
        self.assertIn("transit_times", ext)
        self.assertIn("climate", ext)
        self.assertIn("cost_of_living", ext)
        self.assertIn("student_reviews", ext)
        self.assertTrue(len(ext["student_reviews"]) > 0)

    def test_05_trust_scoring(self):
        """Test multi-factor trust score calculation and tier classification."""
        item = {
            "title": "Al-Farabi Kazakh National University Campus Tower Almaty",
            "source_url": "https://commons.wikimedia.org/wiki/File:KazNU_Tower.jpg",
            "source_api": "wikimedia",
            "confidence": 0.90
        }
        trust_res = calculate_trust_score(item, "Казахский национальный университет имени аль-Фараби", "Алматы")
        self.assertIn("trust_score", trust_res)
        self.assertTrue(trust_res["trust_score"] >= 80, f"Expected high trust, got {trust_res['trust_score']}")
        self.assertEqual(trust_res["trust_tier"], "high")
        self.assertIn("Высокая", trust_res["trust_label"])

    def test_06_campus_summary(self):
        """Test generation of honest campus summary."""
        canonical = "Казахский национальный университет имени аль-Фараби"
        city = "Алматы"
        country = "Казахстан"
        categories = {
            "campus": {"is_verified": True, "items_count": 3},
            "dormitory": {"is_verified": False, "items_count": 0},
            "lecture_hall": {"is_verified": False, "items_count": 0},
            "library": {"is_verified": True, "items_count": 1},
            "city": {"is_verified": True, "items_count": 1},
            "sport": {"is_verified": False, "items_count": 0},
            "labs": {"is_verified": False, "items_count": 0},
            "student_life": {"is_verified": False, "items_count": 0}
        }
        sources_status = {"wikimedia": "ok (10 items)", "openverse": "timeout"}

        summary = _generate_rule_based_summary(canonical, city, country, categories, sources_status)
        self.assertIn("Казахский", summary)
        self.assertIn("Алматы", summary)
        self.assertIn("Нет верифицированных данных", summary)

    def test_07_pdf_report_generation(self):
        """Test White-Label PDF report generation via ReportLab with UTF-8 Cyrillic text."""
        profile_mock = {
            "canonical_name": "Казахский национальный университет имени аль-Фараби",
            "english_name": "Al-Farabi Kazakh National University",
            "short_name": "КазНУ",
            "city": "Алматы",
            "country": "Казахстан",
            "campus_summary": "Кампус КазНУ расположен в Алматы. Подтверждены учебные корпуса и библиотека.",
            "sources_status": {"wikimedia": "ok (14 items)", "openverse": "timeout (skipped)"},
            "metrics": {"duplicates_dropped": 2},
            "rules_summary": {"verification_coverage_percent": 50.0, "total_verified_photos": 4},
            "categories": {
                "campus": {
                    "title": "Кампус / Корпуса",
                    "description": "Фасады учебных корпусов",
                    "is_verified": True,
                    "items_count": 2,
                    "average_confidence": 0.89,
                    "items": [
                        {
                            "id": "item1",
                            "title": "Главный корпус ректората",
                            "confidence": 0.91,
                            "license_name": "CC BY-SA 4.0",
                            "source_url": "https://commons.wikimedia.org/wiki/File:Kaznu.jpg",
                            "author": "Kenjeke",
                            "source_api": "wikimedia"
                        }
                    ]
                },
                "dormitory": {
                    "title": "Общежития",
                    "description": "Студенческие общежития",
                    "is_verified": False,
                    "items_count": 0,
                    "items": []
                }
            }
        }

        pdf_bytes = build_pdf_report(profile_mock)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 2000, "PDF should be generated and non-empty")
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Output must be valid PDF format")

    async def test_08_web_search_info_and_images(self):
        """Test internet search engine cascade, facts extraction, and web image aggregation."""
        from core.web_search import search_university_info, search_university_images
        from core.aggregator import aggregate_media

        # 1. Test search_university_info structure and facts
        facts = await search_university_info("University of Tartu")
        self.assertIn("canonical_name", facts)
        self.assertIn("coordinates", facts)
        self.assertIn("lat", facts["coordinates"])
        self.assertIn("lon", facts["coordinates"])
        self.assertIn("sources", facts)
        self.assertIn("description", facts)

        # 2. Test web image search output format
        web_images = await search_university_images("University of Tartu", limit=3)
        self.assertIsInstance(web_images, list)
        if len(web_images) > 0:
            first = web_images[0]
            self.assertIn("preview_url", first)
            self.assertEqual(first.get("source_api"), "web_search")
            self.assertIn("license_name", first)

        # 3. Test aggregator integration with web_search source status
        disambig_mock = {
            "canonical_name": "University of Tartu",
            "english_name": "University of Tartu",
            "search_keywords": ["University of Tartu campus"],
            "coordinates": {"lat": 58.3806, "lon": 26.7251},
            "city": "Tartu",
            "country": "Estonia"
        }
        items, statuses = await aggregate_media(disambig_mock)
        self.assertIn("web_search", statuses)

        # 4. Test campus extended data enrichment with web_facts
        ext_with_facts = get_campus_extended_data(
            "University of Tartu",
            "Tartu",
            "Estonia",
            {"lat": 58.3806, "lon": 26.7251},
            web_facts={
                "founded_year": "1632",
                "students_count": "14000",
                "website": "https://ut.ee",
                "description": "Oldest university in Estonia"
            }
        )
        self.assertIn("1632", ext_with_facts["student_reviews"][0]["text"])
        self.assertIn("ut.ee", ext_with_facts["student_reviews"][0]["text"])

if __name__ == "__main__":
    unittest.main()
