from aiohttp_session import get_session
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPConflict
from aiohttp_apispec import request_schema, response_schema

from app.quiz.schemes import ThemeListSchema, ThemeSchema
from app.web.app import View
from app.web.utils import json_response

from aiohttp import web

import json

from app.quiz.models import Answer

from aiohttp_session import get_session
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema

from app.quiz.schemes import QuestionSchema
from app.web.utils import json_response

from app.quiz.schemes import ListQuestionSchema

from aiohttp.web_exceptions import HTTPUnprocessableEntity

class ThemeAddView(View):
    async def post(self):
        session = await get_session(self.request)
        if "admin_email" not in session:
            raise HTTPUnauthorized()

        try:
            data = await self.request.json()
        except Exception:
            raise HTTPBadRequest(reason="Invalid JSON body")

        if "title" not in data:
            return web.json_response(
                {
                    "status": "bad_request",
                    "message": "Unprocessable Entity",
                    "data": {
                        "json": {
                            "title": ["Missing data for required field."]
                        }
                    }
                },
                status=400
            )

        title = data["title"]

        existing = await self.store.quizzes.get_theme_by_title(title)
        if existing:
            raise HTTPConflict(reason="Theme already exists")

        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))



class ThemeListView(View):
    async def get(self):
        print("ThemeListView called", flush=True)
        session = await get_session(self.request)
        if "admin_email" not in session:
            raise HTTPUnauthorized()

        themes = await self.store.quizzes.list_themes()
        data = [ThemeSchema().dump(theme) for theme in themes]

        return json_response(data={"themes": data})


class QuestionAddView(View):
    async def post(self):
        session = await get_session(self.request)
        if "admin_email" not in session:
            raise HTTPUnauthorized()

        try:
            data = await self.request.json()
        except Exception:
            raise HTTPBadRequest(reason="Invalid JSON body")

        title = data.get("title")
        theme_id = data.get("theme_id")
        answers_data = data.get("answers", [])

        if not isinstance(answers_data, list) or len(answers_data) < 2:
            return web.json_response(
                {
                    "status": "bad_request",
                    "message": "Invalid answers: at least 2 required",
                    "data": {}
                },
                status=400
            )

        correct_answers = [a for a in answers_data if a.get("is_correct") is True]
        if len(correct_answers) != 1:
            return web.json_response(
                {
                    "status": "bad_request",
                    "message": "Exactly one correct answer required",
                    "data": {}
                },
                status=400
            )

        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            return web.json_response(
                {
                    "status": "not_found",
                    "message": "Theme not found",
                    "data": {}
                },
                status=404
            )

        answers = [
            Answer(title=a["title"], is_correct=a["is_correct"])
            for a in answers_data
        ]

        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=answers,
        )

        return json_response(data=QuestionSchema().dump(question))



class QuestionListView(View):
    async def get(self):
        session = await get_session(self.request)
        print("SESSION IN GET", session, flush=True)
        if "admin_email" not in session:
            raise HTTPUnauthorized()

        print(self.request)

        theme_id = self.request.query.get("theme_id")
        theme_id = int(theme_id) if theme_id else None

        print(theme_id)

        questions = await self.store.quizzes.list_questions(theme_id=theme_id)

        return json_response(data={"questions": [
            QuestionSchema().dump(q) for q in questions
        ]})
