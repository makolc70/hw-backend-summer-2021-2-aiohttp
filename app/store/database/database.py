from dataclasses import dataclass, field

from app.quiz.models import Theme, Question

@dataclass
class Database:
    # TODO: добавить поля admins и questions
    themes: list[Theme] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    #admins: list[Admin] = field(default_factory=list)  # опционально

    @property
    def next_theme_id(self) -> int:
        return len(self.themes) + 1

    _question_id_counter: int = 1

    def next_question_id(self) -> int:
        id_ = self._question_id_counter
        self._question_id_counter += 1
        return id_

    def clear(self):
        self.themes.clear()
        self.questions.clear()
