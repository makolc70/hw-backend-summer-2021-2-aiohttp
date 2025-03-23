from app.store import Store
from app.web.config import Config
import pytest
from aiohttp import web


pytestmark = pytest.mark.asyncio

class TestAdminAccessor:
    async def test_admin_created_on_startup(
        self, store: Store, config: Config
    ) -> None:
        admin = await store.admins.get_by_email(config.admin.email)
        print("ADMIN = ", admin)

        assert admin is not None
        assert admin.email == config.admin.email
        assert (
            admin.password != config.admin.password
        )
        assert admin.id == 1
