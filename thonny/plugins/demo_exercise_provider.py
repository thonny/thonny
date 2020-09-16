from typing import Tuple, List, Dict, Any

from thonny import get_workbench
from thonny.exercises import ExerciseProvider, FormData, EDITOR_CONTENT_NAME


class DemoExerciseProvider(ExerciseProvider):
    def __init__(self, exercises_view):
        self.exercises_view = exercises_view

    def get_html_and_breadcrumbs(
        self, url: str, form_data: FormData
    ) -> Tuple[str, List[Tuple[str, str]]]:
        if url == "/ex1":
            return (self._get_ex_text(1), [("/ex1", "Ülesanne 1")])
        elif url == "/ex2":
            return (self._get_ex_text(2), [("/ex2", "Ülesanne 2")])
        elif url == "/ex1/submit":
            return (self._get_submit_text(form_data), [("/ex1", "Ülesanne 1")])
        elif url == "/ex2/submit":
            return (self._get_submit_text(form_data), [("/ex1", "Ülesanne 1")])
        else:
            return (self._get_ex_list(), [])

    def _get_ex_list(self):
        return """
            <ul>
                <li><a href="/ex1">Ülesanne 1</a></li>
                <li><a href="/ex2">Ülesanne 2</a></li>
            </ul>
        """

    def _get_ex_text(self, num):

        return """
    <h1>Ülesanne {num}</h>
    <p>blaa, blah</p>
    <p>blaa, blaa, blah</p>

    <form action="/ex{num}/submit">
    <input type="hidden" name="{editor_content_name}" />
    <input type="submit" value="Esita aktiivse redaktori sisu" />
    </form>

    """.format(
            num=num, editor_content_name=EDITOR_CONTENT_NAME
        )

    def _get_submit_text(self, form_data):
        print("FD", form_data)
        source = form_data.get(EDITOR_CONTENT_NAME)

        return """
        <h1>Esitus</h1>
        <code>
{source}
        </code>
        <h2>Tulemus</h2>
        Priima töö!
        
        <h2>Eelmised esitused</h2>
        <ul>
            <li>2020-09-01 12:12:12</li>
        </ul>
        """.format(
            source=source
        )


def load_plugin():
    get_workbench().add_exercise_provider("demo", "Demo provider", DemoExerciseProvider)
