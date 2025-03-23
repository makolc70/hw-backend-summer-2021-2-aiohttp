import typing
from mailbox import Message

from app.store.vk_api.dataclasses import Update
from app.store.vk_api.dataclasses import Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        if not updates:
            return

        for update in updates:
            if update.type == "message_new":
                user_id = update.object.message.from_id
                text = "some text"
                await self.app.store.vk_api.send_message(
                    Message(user_id=user_id, text=text)
                )
            pass
