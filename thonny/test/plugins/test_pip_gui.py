import pytest

from thonny.plugins.pip_gui import PluginsPipDialog, _EXTRA_MARKER_RE


@pytest.mark.parametrize(
    "requirement, conflicts",
    [
        ("thonny>=4.0", False),
        ("thonny", False),
        ("thonny!=4.1.0", True),
        ("thonny==4.1.0.1", True),
        ("thonny>=4,<5", False),
        ("thonny==4.1.*", False),
        ("thonny==4.1", False),
        ("Thonny>=5", True),
        ("thonnyfoo>=5", False),
        ("thonny-plugin>=5", False),
        ('thonny>=5; python_version < "2"', False),
        ('thonny>=5; python_version >= "3"', True),
        ('thonny>=5; extra == "dev"', False),
    ],
)
def test_conflicts_with_thonny_version(monkeypatch, requirement, conflicts):
    monkeypatch.setattr("thonny.get_version", lambda: "4.1.0")
    assert PluginsPipDialog._conflicts_with_thonny_version(None, [requirement]) == (
        [requirement] if conflicts else []
    )


def test_conflicts_with_thonny_prerelease(monkeypatch):
    monkeypatch.setattr("thonny.get_version", lambda: "5.0.0b1")
    assert PluginsPipDialog._conflicts_with_thonny_version(None, ["thonny>=4"]) == []


def test_extra_marker_re() -> None:
    for text in [
        "extra == 'dev'",
        r"extra == 'dev \' with quote'",
        "  extra  ==  'dev'  ",
        'extra == "dev"',
        r'extra == "dev \"with quote"',
    ]:
        assert _EXTRA_MARKER_RE.match(text) is not None
