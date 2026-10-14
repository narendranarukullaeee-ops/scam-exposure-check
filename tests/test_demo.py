"""The static demo page (docs/index.html) must match what the scoring engine produces."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("build_demo", ROOT / "scripts" / "build_demo.py")
build_demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_demo)


def test_demo_page_is_up_to_date():
    page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert page == build_demo.render(full=True), "Demo page is stale. Run: python scripts/build_demo.py"


def test_demo_people_cover_low_medium_and_high():
    levels = {p["result"]["level"] for p in build_demo.build_data()["people"]}
    assert {"LOW", "MEDIUM", "HIGH"} <= levels
