from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_agents_requires_website_sync_for_skill_changes() -> None:
    source = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    normalized = " ".join(source.split())

    for change in ("add", "modify", "delete"):
        assert change in source

    for lifecycle_rule in (
        "user-visible behavior changes",
        "remove its canonical catalog entry",
        "every locale entry",
    ):
        assert lifecycle_rule in normalized

    for required_path in (
        "website/src/data/skills.ts",
        "website/src/i18n/content/ko.json",
        "website/src/i18n/content/en.json",
        "website/src/i18n/content/jp.json",
        "website/src/i18n/content/cn.json",
        "website/scripts/generate-social-cards.mjs",
    ):
        assert required_path in source

    for command in (
        "npm --prefix website run verify:catalog",
        "npm --prefix website run verify:locales",
        "npm --prefix website run build",
    ):
        assert command in source


def test_build_reinstall_is_present_in_catalog_and_every_locale() -> None:
    sources = [
        ROOT / "website" / "src" / "data" / "skills.ts",
        *(
            ROOT / "website" / "src" / "i18n" / "content" / f"{locale}.json"
            for locale in ("ko", "en", "jp", "cn")
        ),
    ]

    for path in sources:
        assert '"build-reinstall"' in path.read_text(encoding="utf-8")
