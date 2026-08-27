from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_app_loads_without_exceptions() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=10).run()
    assert not app.exception
    assert any("Serving S.A.S." in title.value for title in app.title)


def test_default_example_produces_recommendations() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=10).run()
    app.button[0].click().run()
    assert not app.exception
    assert any("Resumen del resorte actual" in heading.value for heading in app.subheader)
    assert len(app.metric) >= 7
    assert len(app.dataframe) >= 2
    assert any(
        "Alternativa económica" in heading.value for heading in app.markdown
    )
