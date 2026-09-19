import uuid
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

logger = logging.getLogger("truecampus.auth")

auth_router = APIRouter(prefix="/api", tags=["auth_credits"])

INITIAL_FREE_CREDITS = 5
ANALYSIS_COST_CREDITS = 1

PROMO_CODES: Dict[str, int] = {
    "CAMPUS2026": 5,
    "STUDENT": 5,
    "LOCUS": 10,
    "HACKATHON": 15,
    "ALMATY": 5,
    "ASTANA": 5
}

USERS_STORE: Dict[str, Dict[str, Any]] = {
    "demo@truecampus.io": {
        "id": "u_demo",
        "name": "Айбек Нурланов",
        "email": "demo@truecampus.io",
        "password": "password123",
        "role": "Студент",
        "credits": 8,
        "token": "token_demo_user",
        "used_promos": ["CAMPUS2026"]
    }
}

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "Абитуриент"

class LoginRequest(BaseModel):
    email: str
    password: str

class TopUpRequest(BaseModel):
    package_id: str
    credits: int
    amount_kzt: Optional[int] = 0

class PromoCodeRequest(BaseModel):
    code: str

def find_user_by_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    token_clean = token.replace("Bearer ", "").strip()
    for user in USERS_STORE.values():
        if user.get("token") == token_clean:
            return user
    return None

def find_user_by_email(email: Optional[str]) -> Optional[Dict[str, Any]]:
    if not email:
        return None
    return USERS_STORE.get(email.strip().lower())

def get_current_user_from_auth(auth_header: Optional[str], email_param: Optional[str] = None) -> Optional[Dict[str, Any]]:
    user = find_user_by_token(auth_header)
    if not user and email_param:
        user = find_user_by_email(email_param)
    return user

@auth_router.post("/auth/register")
async def register(payload: RegisterRequest):
    email = payload.email.strip().lower()
    name = payload.name.strip()
    password = payload.password.strip()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Укажите корректный email адрес")
    if not name:
        raise HTTPException(status_code=400, detail="Укажите ваше имя")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Пароль должен содержать не менее 4 символов")

    if email in USERS_STORE:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже зарегистрирован")

    user_id = f"u_{str(uuid.uuid4())[:8]}"
    token = f"token_{str(uuid.uuid4())[:16]}"

    user_data = {
        "id": user_id,
        "name": name,
        "email": email,
        "password": password,
        "role": payload.role or "Абитуриент",
        "credits": INITIAL_FREE_CREDITS,
        "token": token,
        "used_promos": []
    }
    USERS_STORE[email] = user_data

    logger.info(f"New user registered: {email} with {INITIAL_FREE_CREDITS} initial credits")

    return {
        "success": True,
        "status": "success",
        "user": {
            "id": user_data["id"],
            "name": user_data["name"],
            "email": user_data["email"],
            "role": user_data["role"],
            "credits": user_data["credits"]
        },
        "token": token,
        "credits": user_data["credits"]
    }

@auth_router.post("/auth/login")
async def login(payload: LoginRequest):
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Укажите корректный email")

    user = USERS_STORE.get(email)
    if not user:
        user_id = f"u_{str(uuid.uuid4())[:8]}"
        token = f"token_{str(uuid.uuid4())[:16]}"
        user = {
            "id": user_id,
            "name": email.split("@")[0].capitalize(),
            "email": email,
            "password": password,
            "role": "Абитуриент",
            "credits": INITIAL_FREE_CREDITS,
            "token": token,
            "used_promos": []
        }
        USERS_STORE[email] = user
    else:
        if user["password"] != password and user["password"] != "password123":
            raise HTTPException(status_code=401, detail="Неверный пароль")
        if not user.get("token"):
            user["token"] = f"token_{str(uuid.uuid4())[:16]}"

    logger.info(f"User logged in: {email} (balance: {user.get('credits', 0)} credits)")

    return {
        "success": True,
        "status": "success",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "Абитуриент"),
            "credits": user.get("credits", 0)
        },
        "token": user["token"],
        "credits": user.get("credits", 0)
    }

@auth_router.get("/auth/me")
async def auth_me(authorization: Optional[str] = Header(None), email: Optional[str] = None):
    user = get_current_user_from_auth(authorization, email)
    if not user:
        return {"authenticated": False, "user": None, "credits": 0}

    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "Абитуриент"),
            "credits": user.get("credits", 0)
        },
        "credits": user.get("credits", 0)
    }

@auth_router.get("/user/credits")
async def get_credits(authorization: Optional[str] = Header(None), email: Optional[str] = None):
    user = get_current_user_from_auth(authorization, email)
    if not user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return {
        "credits": user.get("credits", 0),
        "user_email": user["email"]
    }

@auth_router.post("/user/credits/deduct")
async def deduct_credit(authorization: Optional[str] = Header(None), email: Optional[str] = None):
    user = get_current_user_from_auth(authorization, email)
    if not user:
        raise HTTPException(status_code=401, detail="Для проверки университета необходимо войти в аккаунт")

    current_balance = user.get("credits", 0)
    if current_balance < ANALYSIS_COST_CREDITS:
        raise HTTPException(
            status_code=402,
            detail="Кредиты закончились! Пожалуйста, пополните баланс для продолжения проверок."
        )

    user["credits"] = current_balance - ANALYSIS_COST_CREDITS
    logger.info(f"Deducted 1 credit from {user['email']}. Remaining: {user['credits']}")

    return {
        "success": True,
        "deducted": ANALYSIS_COST_CREDITS,
        "remaining_credits": user["credits"]
    }

@auth_router.post("/user/credits/topup")
async def topup_credits(payload: TopUpRequest, authorization: Optional[str] = Header(None), email: Optional[str] = None):
    user = get_current_user_from_auth(authorization, email)
    if not user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    add_credits = max(1, payload.credits)
    user["credits"] = user.get("credits", 0) + add_credits
    logger.info(f"Top-up {add_credits} credits for {user['email']}. New balance: {user['credits']}")

    return {
        "success": True,
        "added": add_credits,
        "credits": user["credits"],
        "package_id": payload.package_id,
        "message": f"Баланс успешно пополнен на +{add_credits} кредитов!"
    }

@auth_router.post("/user/credits/promo")
async def apply_promo(payload: PromoCodeRequest, authorization: Optional[str] = Header(None), email: Optional[str] = None):
    user = get_current_user_from_auth(authorization, email)
    if not user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    code_clean = payload.code.strip().upper()
    if code_clean not in PROMO_CODES:
        raise HTTPException(status_code=400, detail="Неверный или недействительный промокод")

    used_promos = user.setdefault("used_promos", [])
    if code_clean in used_promos:
        raise HTTPException(status_code=400, detail="Вы уже использовали этот промокод")

    bonus_credits = PROMO_CODES[code_clean]
    user["credits"] = user.get("credits", 0) + bonus_credits
    used_promos.append(code_clean)

    logger.info(f"Promo {code_clean} applied for {user['email']}: +{bonus_credits} credits")

    return {
        "success": True,
        "code": code_clean,
        "bonus_credits": bonus_credits,
        "credits": user["credits"],
        "message": f"Промокод активирован! Начислено +{bonus_credits} кредитов."
    }
