import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "make-bot-ui"
SKILL = PACKAGE / "skills" / "make-bot-ui"
SCRIPT = SKILL / "scripts" / "webhook_post.py"

CURSOR_ONLY = (
    "update_state",
    "SendToUser",
    "api2.cursor.sh",
    "subagent_type: comment-sicko",
    "~/.cursor/rules",
    "Bugbot",
    "cursor-team-kit",
    "the Task tool",
    "pstack",
    "poteto",
    "backnotprop",
    "mattpocock",
    "cursor/plugins",
)

GATES = (
    "The webhook URL comes from the user.",
    "The sender key stays in server-side config.",
    "A key pasted in chat is refused.",
    "Do not place the key in the page or the transcript.",
    "The local server, not the browser, sends the POST.",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flat(text: str) -> str:
    return " ".join(text.split())


def load_webhook_post():
    spec = importlib.util.spec_from_file_location("webhook_post", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MakeBotUiSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            PACKAGE / "commands" / "make-bot-ui.md",
            SKILL / "SKILL.md",
            SCRIPT,
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata(self) -> None:
        metadata = json.loads(read(PACKAGE / ".claude-plugin" / "plugin.json"))
        self.assertEqual("make-bot-ui", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])

    def test_interfaces_publish_both_selectors(self) -> None:
        front = read(SKILL / "SKILL.md").split("---\n", 2)[1]
        openai = read(SKILL / "agents" / "openai.yaml")
        command = read(PACKAGE / "commands" / "make-bot-ui.md")
        self.assertIn("name: make-bot-ui\n", front)
        self.assertIn("description: Use when", front)
        self.assertIn("/make-bot-ui", front)
        self.assertIn("$make-bot-ui", front)
        self.assertNotIn("disable-model-invocation", front)
        self.assertIn("$make-bot-ui", openai)
        self.assertIn("Use the **make-bot-ui** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "[webhook url]"', command)

    def test_skill_and_command_state_the_webhook_gates_without_cursor_calls(self) -> None:
        skill = flat(read(SKILL / "SKILL.md"))
        command = flat(read(PACKAGE / "commands" / "make-bot-ui.md"))
        for gate in GATES:
            with self.subTest(gate=gate):
                self.assertIn(gate, skill)
                self.assertIn(gate, command)
        shipped = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PACKAGE.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"}
        )
        for token in CURSOR_ONLY:
            with self.subTest(token=token):
                self.assertNotIn(token, shipped)

    def test_evals_cover_the_gates(self) -> None:
        payload = json.loads(read(SKILL / "evals" / "evals.json"))
        evals = payload["evals"]
        self.assertEqual("make-bot-ui", payload["skill_name"])
        self.assertGreaterEqual(len(evals), 3)
        for item in evals:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        joined = json.dumps(evals, ensure_ascii=False)
        for gate in ("research-brief", "server-side config", "pasted"):
            with self.subTest(gate=gate):
                self.assertIn(gate, joined)

    def test_chann_routes_a_bot_ui_request_to_feature(self) -> None:
        text = read(ROOT / "chann-mode" / "skills" / "chann" / "SKILL.md")
        routing = text.split("## 2. Routing", 1)[1].split("## 3. Principles", 1)[0]
        row = [line for line in routing.splitlines() if "`make-bot-ui`" in line]
        self.assertEqual(1, len(row))
        self.assertIn("| feature |", row[0])

    def test_page_cannot_carry_the_key_and_the_server_sends_the_post(self) -> None:
        webhook = load_webhook_post()
        key = "wk_" + "9c1e0b7f3a" + "44"
        url = "https://hooks.example.test/wake"
        page = webhook.render_page("Desk", [{"id": "ping", "label": "Ping"}])
        webhook.reject_page(page, key=key, webhook_url=url)
        self.assertIn('action="/send/ping"', page)
        self.assertNotIn(key, page)
        self.assertNotIn("hooks.example.test", page)

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "server.json"
            config_path.write_text(json.dumps({"url": url, "key": key}), encoding="utf-8")
            config = webhook.load_server_config(config_path)

        post = webhook.build_server_post(config, {"action": "ping"})
        self.assertEqual("POST", post["method"])
        self.assertEqual(url, post["url"])
        self.assertEqual("Bearer " + key, post["headers"]["Authorization"])
        self.assertNotIn(key, post["body"])
        self.assertEqual({"action": "ping"}, json.loads(post["body"]))
        self.assertEqual(8, post["timeout_seconds"])
        self.assertEqual(0, post["retries"])

        poisoned = page.replace("</h1>", f"</h1><p>{key}</p>")
        with self.assertRaises(webhook.KeyLeak) as leaked:
            webhook.reject_page(poisoned, key=key, webhook_url=url)
        self.assertNotIn(key, str(leaked.exception))

        hosted = page.replace("</h1>", "</h1><form action=\"https://hooks.example.test/wake\">")
        with self.assertRaises(webhook.KeyLeak):
            webhook.reject_page(hosted, key=key, webhook_url=url)

        with self.assertRaises(webhook.KeyLeak) as body_leak:
            webhook.build_server_post(config, {"note": key})
        self.assertNotIn(key, str(body_leak.exception))

        refusal = webhook.refuse_pasted_key(f"the sender key is {key}", key)
        self.assertTrue(refusal)
        self.assertNotIn(key, refusal)
        self.assertEqual("", webhook.refuse_pasted_key("the URL is fine", key))

    def test_config_rejects_a_missing_key_or_an_http_url(self) -> None:
        webhook = load_webhook_post()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "server.json"
            path.write_text(json.dumps({"url": "http://hooks.example.test/wake", "key": "abc"}), encoding="utf-8")
            with self.assertRaises(webhook.ConfigError):
                webhook.load_server_config(path)
            path.write_text(json.dumps({"url": "https://hooks.example.test/wake", "key": "  "}), encoding="utf-8")
            with self.assertRaises(webhook.ConfigError):
                webhook.load_server_config(path)


if __name__ == "__main__":
    unittest.main()
