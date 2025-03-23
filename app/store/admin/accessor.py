import typing
import hashlib
from aiohttp import web


from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class AdminAccessor(BaseAccessor):
    def __init__(self, app: "Application"):
        super().__init__(app)
        self.admin: Admin | None = None

    async def connect(self, app: "Application") -> None:
        admin_config = app.config.admin
        if not admin_config:
            raise ValueError("Admin configuration is missing in config.yml")

        hashed_password = hash_password(admin_config.password)
        self.admin = Admin(email=admin_config.email, password=hashed_password, id=1)
        print("Admin initialized from config.")

    async def get_by_email(self, email: str) -> Admin | None:
        print("In get_by_email, self.admin =", self.admin)
        if self.admin and self.admin.email == email:
            return self.admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        if self.admin and self.admin.email == email and self.admin.password == password:
            return self.admin
        return None
