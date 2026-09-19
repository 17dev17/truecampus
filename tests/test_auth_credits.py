# -*- coding: utf-8 -*-
"""
Tests for TrueCampus Authentication, Credits System, and Analysis Guard.
"""

import os
import sys
import unittest
import pytest
from httpx import AsyncClient, ASGITransport

# Ensure truecampus path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from core.auth_credits import USERS_STORE, INITIAL_FREE_CREDITS

@pytest.mark.anyio
class TestAuthCredits(unittest.IsolatedAsyncioTestCase):

    async def test_01_registration_grants_initial_credits(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            email = "student_test@truecampus.io"
            resp = await ac.post("/api/auth/register", json={
                "name": "Тестовый Студент",
                "email": email,
                "password": "strongpassword123",
                "role": "Абитуриент"
            })
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["credits"], INITIAL_FREE_CREDITS)
            self.assertIn("token", data)
            self.assertEqual(data["user"]["email"], email)

    async def test_02_login_returns_user_and_credits(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/api/auth/login", json={
                "email": "demo@truecampus.io",
                "password": "password123"
            })
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertTrue(data["success"])
            self.assertTrue(data["credits"] > 0)
            self.assertIn("token", data)

    async def test_03_unauthorized_analyze_is_blocked(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Attempt to analyze without auth credentials
            resp = await ac.post("/api/analyze", json={
                "query": "MIT"
            })
            self.assertEqual(resp.status_code, 401)
            self.assertIn("Регистрация обязательна", resp.json()["detail"])

    async def test_04_authorized_analyze_deducts_one_credit(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Login as demo
            login_resp = await ac.post("/api/auth/login", json={
                "email": "demo@truecampus.io",
                "password": "password123"
            })
            token = login_resp.json()["token"]
            initial_credits = login_resp.json()["credits"]

            # Analyze university with token
            analyze_resp = await ac.post("/api/analyze", 
                headers={"Authorization": f"Bearer {token}"},
                json={"query": "КазНУ им. Аль-Фараби", "user_email": "demo@truecampus.io"}
            )
            self.assertEqual(analyze_resp.status_code, 200)
            data = analyze_resp.json()
            self.assertIn("canonical_name", data)
            self.assertEqual(data["user_remaining_credits"], initial_credits - 1)

    async def test_05_zero_credits_blocks_analysis_and_prompts_topup(self):
        # Create zero credit user
        zero_user_email = "zero_credits@truecampus.io"
        USERS_STORE[zero_user_email] = {
            "id": "u_zero",
            "name": "Zero User",
            "email": zero_user_email,
            "password": "password123",
            "credits": 0,
            "token": "token_zero_credits",
            "used_promos": []
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/api/analyze",
                headers={"Authorization": "Bearer token_zero_credits"},
                json={"query": "MIT", "user_email": zero_user_email}
            )
            self.assertEqual(resp.status_code, 402)
            self.assertIn("Кредиты закончились", resp.json()["detail"])

    async def test_06_topup_and_promo_codes(self):
        promo_user_email = "promo_user@truecampus.io"
        USERS_STORE[promo_user_email] = {
            "id": "u_promo",
            "name": "Promo User",
            "email": promo_user_email,
            "password": "password123",
            "credits": 0,
            "token": "token_promo_user",
            "used_promos": []
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Top-up package
            topup_resp = await ac.post("/api/user/credits/topup",
                headers={"Authorization": "Bearer token_promo_user"},
                json={"package_id": "pkg_student", "credits": 15, "amount_kzt": 1500}
            )
            self.assertEqual(topup_resp.status_code, 200)
            self.assertEqual(topup_resp.json()["credits"], 15)

            # Apply promo code CAMPUS2026 (+5 credits)
            promo_resp = await ac.post("/api/user/credits/promo",
                headers={"Authorization": "Bearer token_promo_user"},
                json={"code": "CAMPUS2026"}
            )
            self.assertEqual(promo_resp.status_code, 200)
            self.assertEqual(promo_resp.json()["credits"], 20)

            # Applying again should fail
            dup_resp = await ac.post("/api/user/credits/promo",
                headers={"Authorization": "Bearer token_promo_user"},
                json={"code": "CAMPUS2026"}
            )
            self.assertEqual(dup_resp.status_code, 400)
