import json
import hashlib
from aiohttp import web
from aiohttp.web import View
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp.web_exceptions import (
    HTTPUnprocessableEntity,
    HTTPForbidden,
    HTTPUnauthorized,
    HTTPBadRequest,
)

from app.web.config import Config
from app.store.admin.accessor import AdminAccessor


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    print("PASS = ", plain, " ", hashed)
    return plain == hashed


class AdminLoginView(View):
    async def post(self):
        print("AdminLoginView.post started", flush=True)
        try:
            data = await self.request.json()
            print("Received data:", data, flush=True)
        except Exception as e:
            print("Error reading JSON:", e, flush=True)
            raise HTTPBadRequest(reason="Invalid JSON body")

        email = data.get("email")
        password = data.get("password")

        if not email:
            detail = {"json": {"email": ["Missing data for required field."]}}
            raise HTTPUnprocessableEntity(
                reason="Unprocessable Entity", text=json.dumps(detail)
            )
        if not password:
            detail = {"json": {"password": ["Missing data for required field."]}}
            raise HTTPUnprocessableEntity(
                reason="Unprocessable Entity", text=json.dumps(detail)
            )

        print("loaded a config...")

        passwd = self.request.app.config.admin.password
        usr = self.request.app.config.admin.email
        print(usr, email)

        if email == usr and verify_password(password, passwd):

            session = await get_session(self.request)
            print("got session")
            session["admin_email"] = email

            return web.json_response({
                "status": "ok",
                "data": {
                    "id": 1,
                    "email": email,
                }
            }, status=200)
        else:
            print("inv cred")
            raise HTTPForbidden(reason="Invalid credentials")

class AdminCurrentView(View):
    async def get(self):
        session = await get_session(self.request)
        admin_email = session.get("admin_email")

        print("session = ")


        if not admin_email:
            raise HTTPUnauthorized(reason="Unauthorized")

        config_admin_email = self.request.app.config.admin.email

        print("COMPARE")

        if admin_email != config_admin_email:
            raise HTTPUnauthorized(reason="Unauthorized")

        return web.json_response({
            "status": "ok",
            "data": {
                "id": 1,
                "email": admin_email,
            }
        }, status=200)
