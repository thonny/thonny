from typing import Tuple, List

from thonny import get_workbench
from thonny.exercises import ExerciseProvider


class DemoExerciseProvider(ExerciseProvider):
    def __init__(self, exercises_view):
        self.exercises_view = exercises_view

    def get_html_and_breadcrumbs(self, url: str) -> Tuple[str, List[Tuple[str, str]]]:
        if url == "/ex1":
            return (self._get_ex_text(1), [("/ex1", "Ülesanne 1")])
        elif url == "/ex2":
            return (self._get_ex_text(2), [("/ex2", "Ülesanne 2")])
        elif url == "/ex1/submit":
            return (self._get_submit_text(), [("/ex1", "Ülesanne 1")])
        elif url == "/ex2/submit":
            return (self._get_submit_text(), [("/ex1", "Ülesanne 1")])
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

    <h2>Esitamine</h2>
    <form action="/ex{num}/submit">
    <input type="file" name="source" />
    <input type="submit" value="Esita" />
    </form>

    """.format(
            num=num
        )

    def _get_submit_text(self):
        return """
        <h1>Tulemus</h1>
        Priima töö!
        
        <h2>Eelmised esitused</h2>
        <ul>
            <li>2020-09-01 12:12:12</li>
        </ul>
        """


def load_plugin():
    get_workbench().add_exercise_provider("demo", "Demo provider", DemoExerciseProvider)
