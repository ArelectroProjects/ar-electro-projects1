from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File, Header, Query
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
import os, logging, uuid, asyncio, secrets
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import requests
import pyotp
import qrcode
import base64
from io import BytesIO

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

JWT_ALGORITHM = "HS256"
ALERT_EMAIL = os.environ.get("ALERT_EMAIL", "arelectroprojects@gmail.com")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
APP_NAME = os.environ.get("APP_NAME", "arelectroprojects")

# ---------- Auth ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=15), "type": "access"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_pending_2fa_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=5), "type": "pending_2fa"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def decode_pending_2fa_token(token: str) -> str:
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "pending_2fa":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired 2FA session")

def set_auth_cookies(response: Response, user: dict):
    access = create_access_token(user["id"], user["email"])
    refresh = create_refresh_token(user["id"])
    response.set_cookie(key="access_token", value=access, httponly=True, secure=True, samesite="none", max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh, httponly=True, secure=True, samesite="none", max_age=604800, path="/")

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0, "totp_secret": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class LoginInput(BaseModel):
    email: str
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

@api_router.post("/auth/change-password")
async def change_password(input: PasswordChange, request: Request):
    user_pub = await get_current_user(request)
    user = await db.users.find_one({"id": user_pub["id"]})
    if not user or not verify_password(input.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": hash_password(input.new_password)}})
    return {"status": "password updated"}

@api_router.post("/auth/login")
async def login(input: LoginInput, request: Request, response: Response):
    email = input.email.strip().lower()
    identifier = f"{request.client.host}:{email}"
    attempts = await db.login_attempts.find_one({"identifier": identifier})
    if attempts and attempts.get("count", 0) >= 5:
        locked_since = datetime.fromisoformat(attempts["updated_at"])
        if datetime.now(timezone.utc) - locked_since < timedelta(minutes=15):
            raise HTTPException(status_code=429, detail="Too many failed attempts. Try again in 15 minutes.")
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(input.password, user["password_hash"]):
        await db.login_attempts.update_one(
            {"identifier": identifier},
            {"$inc": {"count": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")
    await db.login_attempts.delete_one({"identifier": identifier})
    if user.get("totp_enabled"):
        return {"requires_2fa": True, "pending_token": create_pending_2fa_token(user["id"])}
    set_auth_cookies(response, user)
    return {"id": user["id"], "email": email, "name": user.get("name", "Admin"), "role": user.get("role", "admin")}

class TwoFAVerify(BaseModel):
    pending_token: str
    code: str = Field(min_length=6, max_length=6)

@api_router.post("/auth/2fa/verify")
async def verify_2fa_login(input: TwoFAVerify, response: Response):
    user_id = decode_pending_2fa_token(input.pending_token)
    user = await db.users.find_one({"id": user_id})
    if not user or not user.get("totp_enabled") or not user.get("totp_secret"):
        raise HTTPException(status_code=400, detail="2FA not enabled for this account")
    if not pyotp.TOTP(user["totp_secret"]).verify(input.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid authentication code")
    set_auth_cookies(response, user)
    return {"id": user["id"], "email": user["email"], "name": user.get("name", "Admin"), "role": user.get("role", "admin")}

@api_router.post("/auth/2fa/setup")
async def setup_2fa(request: Request):
    user = await get_current_user(request)
    secret = pyotp.random_base32()
    await db.users.update_one({"id": user["id"]}, {"$set": {"totp_secret": secret, "totp_enabled": False}})
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user["email"], issuer_name="AR ELECTRO Projects")
    buf = BytesIO()
    qrcode.make(uri).save(buf, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return {"secret": secret, "qr": qr_data_url}

class TwoFACode(BaseModel):
    code: str = Field(min_length=6, max_length=6)

@api_router.post("/auth/2fa/enable")
async def enable_2fa(input: TwoFACode, request: Request):
    user = await get_current_user(request)
    full = await db.users.find_one({"id": user["id"]})
    if not full.get("totp_secret"):
        raise HTTPException(status_code=400, detail="Run 2FA setup first")
    if not pyotp.TOTP(full["totp_secret"]).verify(input.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid code — check your authenticator app")
    await db.users.update_one({"id": user["id"]}, {"$set": {"totp_enabled": True}})
    return {"status": "2fa enabled"}

@api_router.post("/auth/2fa/disable")
async def disable_2fa(input: TwoFACode, request: Request):
    user = await get_current_user(request)
    full = await db.users.find_one({"id": user["id"]})
    if not full.get("totp_enabled"):
        return {"status": "2fa already disabled"}
    if not pyotp.TOTP(full["totp_secret"]).verify(input.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid code — check your authenticator app")
    await db.users.update_one({"id": user["id"]}, {"$set": {"totp_enabled": False}})
    return {"status": "2fa disabled"}

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"status": "logged out"}

@api_router.get("/auth/me")
async def me(user=Depends(get_current_user)):
    return user

@api_router.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await db.users.find_one({"id": payload["sub"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token(user["id"], user["email"])
    response.set_cookie(key="access_token", value=access, httponly=True, secure=True, samesite="none", max_age=900, path="/")
    return {"status": "refreshed"}

# ---------- Object storage ----------

STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
storage_key = None

def init_storage(force: bool = False):
    global storage_key
    if storage_key and not force:
        return storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key, "Content-Type": content_type}, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

def get_object(path: str):
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if resp.status_code == 404:
        key = init_storage(force=True)
        resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

MIME_TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}

@api_router.post("/admin/upload")
async def admin_upload(file: UploadFile = File(...), user=Depends(get_current_user)):
    ext = (file.filename.split(".")[-1] if "." in file.filename else "bin").lower()
    content_type = file.content_type or MIME_TYPES.get(ext, "application/octet-stream")
    path = f"{APP_NAME}/uploads/{user['id']}/{uuid.uuid4()}.{ext}"
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    result = await asyncio.to_thread(put_object, path, data, content_type)
    await db.files.insert_one({
        "id": str(uuid.uuid4()), "storage_path": result["path"], "original_filename": file.filename,
        "content_type": content_type, "size": result["size"], "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"path": result["path"]}

@api_router.get("/files/{path:path}")
async def serve_file(path: str):
    record = await db.files.find_one({"storage_path": path, "is_deleted": False}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        data, content_type = await asyncio.to_thread(get_object, path)
    except Exception:
        raise HTTPException(status_code=404, detail="File not available")
    return Response(content=data, media_type=record.get("content_type", content_type))

# ---------- Categories ----------

CATEGORIES_SEED = [
    {"slug": "diploma-project", "title": "Diploma Project", "eyebrow": "01 / FOUNDATION", "desc": "Build-ready concepts with documentation that makes your viva stronger.", "image": "https://images.unsplash.com/photo-1517055729445-fa7d27394b48?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["Working model", "Report", "PPT"]},
    {"slug": "degree-project", "title": "Degree Project", "eyebrow": "02 / ADVANCED", "desc": "Ambitious engineering builds shaped into practical final-year outcomes.", "image": "https://images.unsplash.com/photo-1562976540-78c559c80296?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["IEEE paper", "Source code", "Mentoring"]},
    {"slug": "drone-project", "title": "Drone Project", "eyebrow": "03 / AERIAL", "desc": "Flight, vision and autonomous systems for the next generation of makers.", "image": "https://images.unsplash.com/photo-1604419623656-8ffddaae66b7?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["Robotics", "Flight test", "IoT"]},
    {"slug": "electronics-project", "title": "Electronics Project", "eyebrow": "04 / CIRCUIT", "desc": "From a first schematic to a reliable, working electronics prototype.", "image": "https://images.unsplash.com/photo-1527356900876-cae61d8d8462?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["PCB", "Sensors", "Embedded"]},
    {"slug": "electrical-project", "title": "Electrical Project", "eyebrow": "05 / POWER", "desc": "Power systems and controls explained clearly, safely and completely.", "image": "https://images.unsplash.com/photo-1562976540-78c559c80296?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["Automation", "Control", "Safety"]},
    {"slug": "embedded-project", "title": "Embedded Project", "eyebrow": "06 / CODE + HARDWARE", "desc": "Purposeful firmware meets real-world hardware and measurable results.", "image": "https://images.unsplash.com/photo-1517055729445-fa7d27394b48?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["Microcontroller", "Firmware", "Testing"]},
    {"slug": "mechanical-project", "title": "Mechanical Project", "eyebrow": "07 / MOTION", "desc": "Prototype mechanisms that move from sketchbook to workshop.", "image": "https://images.unsplash.com/photo-1579803080319-43097a84f424?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["CAD", "Fabrication", "Prototype"]},
    {"slug": "biomedical-project", "title": "Biomedical Project", "eyebrow": "08 / HUMAN SYSTEMS", "desc": "Thoughtful technology for monitoring, access and better outcomes.", "image": "https://images.unsplash.com/photo-1527356900876-cae61d8d8462?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["Sensors", "Assistive", "Research"]},
    {"slug": "iot-projects", "title": "IoT Projects", "eyebrow": "09 / CONNECTED", "desc": "Connect sensors, devices and decisions into one intelligent system.", "image": "https://images.unsplash.com/photo-1562976540-78c559c80296?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85", "tags": ["Cloud ready", "Automation", "Dashboard"]},
]

PROJECTS_SEED = [
    {"category": "diploma-project", "title": "Smart Energy Meter", "description": "GSM-based energy meter with live consumption readings and SMS alerts.", "price_hint": "₹2,999 onwards"},
    {"category": "diploma-project", "title": "Automatic Street Light Controller", "description": "LDR + microcontroller switching that cuts power waste automatically.", "price_hint": "₹1,999 onwards"},
    {"category": "degree-project", "title": "Solar MPPT Charge Controller", "description": "Maximum power point tracking for efficient solar charging systems.", "price_hint": "₹5,499 onwards"},
    {"category": "degree-project", "title": "EV Battery Management System", "description": "Cell monitoring, balancing and protection for electric vehicle packs.", "price_hint": "₹6,999 onwards"},
    {"category": "drone-project", "title": "Quadcopter with Live Camera", "description": "Stable flight build with FPV camera feed and flight-test support.", "price_hint": "₹9,999 onwards"},
    {"category": "drone-project", "title": "Payload Delivery Drone", "description": "Autonomous drop mechanism with GPS waypoint navigation.", "price_hint": "₹12,499 onwards"},
    {"category": "electronics-project", "title": "GSM Gas Leak Detector", "description": "Sensor-based detection with instant SMS and buzzer alerts.", "price_hint": "₹2,499 onwards"},
    {"category": "electrical-project", "title": "Automatic Power Factor Correction", "description": "Capacitor bank switching that improves efficiency and avoids penalties.", "price_hint": "₹4,999 onwards"},
    {"category": "embedded-project", "title": "Sign Language to Speech Glove", "description": "Flex-sensor glove converting gestures into spoken words.", "price_hint": "₹5,999 onwards"},
    {"category": "mechanical-project", "title": "Pneumatic Sheet Metal Cutter", "description": "Compressed-air cutting rig with fabrication and report included.", "price_hint": "₹7,499 onwards"},
    {"category": "biomedical-project", "title": "Patient Health Monitoring System", "description": "Heart-rate, SpO2 and temperature tracking with remote dashboard.", "price_hint": "₹4,499 onwards"},
    {"category": "iot-projects", "title": "Smart Home Automation", "description": "App-controlled lights, fans and security over Wi-Fi.", "price_hint": "₹3,999 onwards"},
]

VIDEOS_SEED = [
    {"video_id": "m0XpjDAtdKU", "title": "GSM Gas Leak Detector", "order": 1},
    {"video_id": "H0fhxb5Mcig", "title": "Automatic Power Factor Correction", "order": 2},
    {"video_id": "-xdUtHikxpY", "title": "DIY Electric Cycle", "order": 3},
]

@api_router.get("/categories")
async def list_categories():
    cats = await db.categories.find({}, {"_id": 0}).to_list(100)
    return sorted(cats, key=lambda c: c.get("eyebrow", ""))

class CategoryUpdate(BaseModel):
    image: str = Field(min_length=5)

@api_router.put("/admin/categories/{slug}")
async def update_category(slug: str, input: CategoryUpdate, user=Depends(get_current_user)):
    result = await db.categories.update_one({"slug": slug}, {"$set": {"image": input.image}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "updated", "slug": slug}

# ---------- Projects ----------

@api_router.get("/projects")
async def list_projects(category: Optional[str] = None):
    query = {"category": category} if category else {}
    return await db.projects.find(query, {"_id": 0}).to_list(500)

class ProjectInput(BaseModel):
    category: str
    title: str = Field(min_length=2)
    description: str = Field(min_length=5)
    price_hint: str = ""
    image: str = ""

@api_router.post("/admin/projects")
async def create_project(input: ProjectInput, user=Depends(get_current_user)):
    doc = {"id": str(uuid.uuid4()), **input.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    await db.projects.insert_one(doc.copy())
    doc.pop("_id", None)
    return doc

@api_router.put("/admin/projects/{project_id}")
async def update_project(project_id: str, input: ProjectInput, user=Depends(get_current_user)):
    result = await db.projects.update_one({"id": project_id}, {"$set": input.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "updated", "id": project_id}

@api_router.delete("/admin/projects/{project_id}")
async def delete_project(project_id: str, user=Depends(get_current_user)):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted"}

# ---------- Videos ----------

@api_router.get("/videos")
async def list_videos():
    vids = await db.videos.find({}, {"_id": 0}).to_list(50)
    return sorted(vids, key=lambda v: v.get("order", 99))

class VideoInput(BaseModel):
    video_id: str = Field(min_length=5)
    title: str = Field(min_length=2)

@api_router.post("/admin/videos")
async def create_video(input: VideoInput, user=Depends(get_current_user)):
    max_order = await db.videos.find_one(sort=[("order", -1)])
    doc = {"id": str(uuid.uuid4()), "video_id": input.video_id.strip(), "title": input.title.strip(),
           "order": (max_order.get("order", 0) + 1) if max_order else 1,
           "created_at": datetime.now(timezone.utc).isoformat()}
    await db.videos.insert_one(doc.copy())
    doc.pop("_id", None)
    return doc

@api_router.delete("/admin/videos/{video_id}")
async def delete_video(video_id: str, user=Depends(get_current_user)):
    result = await db.videos.delete_one({"id": video_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"status": "deleted"}

# ---------- Inquiries + email alert ----------

class InquiryCreate(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(min_length=5)
    phone: str = Field(min_length=8)
    requirement: str = Field(min_length=10)

def send_inquiry_email(inquiry: dict):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        logger.warning("RESEND_API_KEY not set — inquiry email alert skipped")
        return
    try:
        import resend
        resend.api_key = api_key
        html = f"""
        <table style="width:100%;font-family:Arial,sans-serif;background:#0a0a0b;padding:32px;">
          <tr><td style="background:#141416;border:1px solid #2a2a2e;padding:32px;">
            <p style="color:#e51a4D;font-size:12px;letter-spacing:3px;margin:0 0 8px;">NEW PROJECT ENQUIRY</p>
            <h2 style="color:#ffffff;margin:0 0 24px;">{inquiry['name']}</h2>
            <p style="color:#a1a1aa;font-size:14px;margin:4px 0;">Email: {inquiry['email']}</p>
            <p style="color:#a1a1aa;font-size:14px;margin:4px 0 20px;">Phone: {inquiry['phone']}</p>
            <p style="color:#e4e4e7;font-size:15px;line-height:1.6;border-left:3px solid #e51a4D;padding-left:16px;">{inquiry['requirement']}</p>
            <p style="color:#71717a;font-size:12px;margin-top:24px;">AR ELECTRO Projects — website enquiry</p>
          </td></tr>
        </table>"""
        resend.Emails.send({"from": SENDER_EMAIL, "to": [ALERT_EMAIL],
                            "subject": f"New enquiry: {inquiry['name']} — AR ELECTRO Projects", "html": html})
        logger.info(f"Inquiry alert emailed to {ALERT_EMAIL}")
    except Exception as e:
        logger.error(f"Inquiry email failed: {e}")

@api_router.post("/inquiries")
async def create_inquiry(input: InquiryCreate):
    inquiry = {"id": str(uuid.uuid4()), **input.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    await db.inquiries.insert_one(inquiry.copy())
    asyncio.create_task(asyncio.to_thread(send_inquiry_email, inquiry))
    return inquiry

@api_router.get("/inquiries")
async def list_inquiries(user=Depends(get_current_user)):
    items = await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return items

# ---------- Root ----------

@api_router.get("/")
async def root():
    return {"message": "AR ELECTRO Projects API"}

# ---------- Startup ----------

async def seed_admin():
    admin_email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    if not admin_email or not admin_password:
        logger.warning("ADMIN_EMAIL/ADMIN_PASSWORD not set — skipping admin seed")
        return
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "id": str(uuid.uuid4()), "email": admin_email, "password_hash": hash_password(admin_password),
            "name": "AR Admin", "role": "admin", "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Admin account seeded")

async def seed_content():
    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many([{**c, "id": str(uuid.uuid4())} for c in CATEGORIES_SEED])
    if await db.projects.count_documents({}) == 0:
        await db.projects.insert_many([{**p, "id": str(uuid.uuid4()), "image": "", "created_at": datetime.now(timezone.utc).isoformat()} for p in PROJECTS_SEED])
    if await db.videos.count_documents({}) == 0:
        await db.videos.insert_many([{**v, "id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat()} for v in VIDEOS_SEED])

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier")
    await seed_admin()
    await seed_content()
    if EMERGENT_KEY:
        try:
            await asyncio.to_thread(init_storage)
            logger.info("Object storage initialized")
        except Exception as e:
            logger.error(f"Storage init failed: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "https://melodic-empanada-add294.netlify.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
