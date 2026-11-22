"""Exercise publication against real, disposable Git repositories."""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "git-skill/skills/git-commit/scripts/push-checkpoint.sh"


class CheckpointPushTest(unittest.TestCase):
    def test_publish_feature_tracking_main_and_verify_remote(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "remote.git"
            local = root / "work"

            def git(*args, cwd=local):
                return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

            git("init", "-q", "--bare", "-b", "main", str(remote), cwd=root)
            git("clone", "-q", str(remote), str(local), cwd=root)
            for key, value in (("user.name", "Test"), ("user.email", "test@example.invalid"),
                               ("commit.gpgsign", "false")):
                git("config", key, value)
            git("commit", "-qm", "base", "--allow-empty")
            git("push", "-qu", "origin", "main")
            base = git("rev-parse", "HEAD")
            git("switch", "-qc", "feature", "--track", "origin/main")
            git("commit", "-qm", "change", "--allow-empty")
            tip = git("rev-parse", "HEAD")
            for branch, commit in (("main", tip), ("feature", base)):
                result = subprocess.run(["sh", SCRIPT, "origin", branch, commit], cwd=local)
                self.assertNotEqual(result.returncode, 0)
            self.assertEqual(git("show-ref", cwd=remote), f"{base} refs/heads/main")
            for _ in range(2):
                subprocess.run(["sh", SCRIPT, "origin", "feature", tip], cwd=local, check=True)
            self.assertEqual(git("rev-parse", "feature", cwd=remote), tip)
            self.assertEqual(git("rev-parse", "main", cwd=remote), base)
            self.assertEqual(git("rev-parse", "--abbrev-ref", "@{u}"), "origin/main")
