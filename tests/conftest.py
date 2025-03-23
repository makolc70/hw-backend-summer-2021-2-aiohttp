import asyncio
import os
import base64
from asyncio import AbstractEventLoop
from collections.abc import Iterator

import pytest
from cryptography import fernet
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp.test_utils import TestClient
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.store.database.database import Database
from app.web.app import Application, setup_app
from app.web.config import Config

from .fixtures import *  # Do not remove this line!

@pytest.fixture(scope="session")
def event_loop(request) -> Iterator[AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def session_secret_key() -> bytes:
    # постоянный ключ на время тестов
    fernet_key = fernet.Fernet.generate_key()
    return base64.urlsafe_b64decode(fernet_key)

@pytest.fixture(scope="session")
def application(session_secret_key) -> Application:
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()
    app.on_startup.append(app.store.admins.connect)
    app.on_shutdown.append(app.store.admins.disconnect)

    setup_session(app, EncryptedCookieStorage(session_secret_key))

    return app



@pytest.fixture
def store(application: Application) -> Store:
    return application.store

@pytest.fixture
def database(application: Application) -> Database:
    return application.database

@pytest.fixture(autouse=True)
def clear_db(application: Application):
    application.database.clear()

@pytest.fixture
def config(application: Application) -> Config:
    return application.config

@pytest.fixture(autouse=True)
def cli(
    aiohttp_client: AiohttpClient,
    event_loop: AbstractEventLoop,
    application: Application,
) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(application))

@pytest.fixture
async def auth_cli(cli: TestClient, config: Config) -> TestClient:
    await cli.post(
        path="/admin.login",
        json={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    return cli
