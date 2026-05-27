import sys
from datetime import datetime, timezone
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PLUGIN_ROOT / "code-review" / "skills" / "diff-viewer" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_diff_report import (  # noqa: E402
    FileDiff,
    assemble_html,
    build_comment_storage_scope,
    build_highlight_seeds,
    detect_language,
    parse_git_diff,
    render_highlight_seeds,
    render_file_diff,
    render_summary,
)


def test_simple_diff_parses_one_file(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    assert len(files) == 1
    file_diff = files[0]
    assert isinstance(file_diff, FileDiff)
    assert file_diff.old_path == "src/foo.py"
    assert file_diff.new_path == "src/foo.py"
    assert file_diff.status == "modified"
    assert len(file_diff.hunks) == 1
    types = [line.kind for line in file_diff.hunks[0].lines]
    assert types == ["ctx", "del", "add", "add", "add", "ctx", "ctx"]


def test_multi_file_diff(load_fixture):
    files = parse_git_diff(load_fixture("multi-file.diff"))
    assert [file_diff.new_path for file_diff in files] == ["a.py", "b.js"]


def test_rename_status(load_fixture):
    files = parse_git_diff(load_fixture("rename.diff"))
    assert files[0].status == "renamed"
    assert files[0].old_path == "old.py"
    assert files[0].new_path == "new.py"


def test_new_file_status(load_fixture):
    files = parse_git_diff(load_fixture("new-file.diff"))
    assert files[0].status == "added"
    assert files[0].old_path == "/dev/null"
    assert files[0].new_path == "added.py"


def test_deleted_file_status(load_fixture):
    files = parse_git_diff(load_fixture("deleted-file.diff"))
    assert files[0].status == "deleted"
    assert files[0].old_path == "removed.py"
    assert files[0].new_path == "/dev/null"


def test_line_numbers(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    lines = files[0].hunks[0].lines
    assert lines[0].old_no == 1 and lines[0].new_no == 1
    assert lines[1].kind == "del" and lines[1].old_no == 2 and lines[1].new_no is None
    assert lines[2].kind == "add" and lines[2].old_no is None and lines[2].new_no == 2


def test_detect_language_common_extensions():
    assert detect_language("src/foo.py") == "python"
    assert detect_language("ui/Button.tsx") == "typescript"
    assert detect_language("LICENSE") == "plaintext"
    assert detect_language(".bashrc") == "bash"
    assert detect_language("Dockerfile") == "dockerfile"


def test_render_summary_counts_added_and_removed_lines(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    summary = render_summary(files)
    assert summary == {"files": 1, "additions": 3, "deletions": 1}


def test_render_file_diff_contains_unified_and_split_views(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    html = render_file_diff(files[0], index=0)
    assert 'data-view="unified"' in html
    assert 'data-view="split"' in html
    assert 'data-language="python"' in html
    assert 'data-highlight-side="before"' in html
    assert 'data-highlight-side="after"' in html
    assert "return &quot;Hello, &quot; + name" in html


def test_highlight_seeds_reconstruct_before_and_after_files(load_fixture):
    files = parse_git_diff(load_fixture("multi-file.diff"))
    seeds = build_highlight_seeds(files)
    assert len(seeds) == 2
    assert seeds[0]["file"] == 0
    assert seeds[0]["lang"] == "python"
    assert "x = 1" in seeds[0]["before"]
    assert "x = 2" in seeds[0]["after"]
    assert seeds[1]["lang"] == "javascript"


def test_render_highlight_seeds_is_safe_json(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    payload = render_highlight_seeds(files)
    assert '"before"' in payload
    assert "</script>" not in payload


def test_assemble_html_embeds_highlight_seeds(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))
    html = assemble_html(files, tmp_path)
    assert 'id="highlight-seeds"' in html
    assert 'data-highlight-file="0"' in html
    assert "splitHighlightedHtml" in html


def test_assemble_html_scopes_comments_to_generated_report(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))
    output_path = tmp_path / ".diffs" / "review.html"

    html = assemble_html(files, tmp_path, report_path=output_path)

    assert str(output_path) in html
    assert "commentScope:" in html
    assert 'const STORAGE_KEY = "diff-viewer:comments:" + commentStorageScope;' in html
    assert 'const STORAGE_KEY = "diff-viewer:comments:" + (repoPath || "default");' not in html


def test_comment_storage_scope_changes_by_generated_report_path(tmp_path):
    created_at = datetime(2026, 5, 28, 1, 2, 3, tzinfo=timezone.utc)
    first = build_comment_storage_scope(tmp_path, tmp_path / ".diffs" / "first.html", created_at)
    second = build_comment_storage_scope(tmp_path, tmp_path / ".diffs" / "second.html", created_at)

    assert str(tmp_path / ".diffs" / "first.html") in first
    assert str(tmp_path / ".diffs" / "second.html") in second
    assert "2026-05-28T01:02:03" in first
    assert first != second


def test_assemble_html_preserves_template_tokens_inside_diff_content(tmp_path):
    diff_text = """diff --git a/example.txt b/example.txt
index 1111111..2222222 100644
--- a/example.txt
+++ b/example.txt
@@ -1 +1 @@
-old
+__COMMENT_STORAGE_SCOPE__ __DEFAULT_VIEW__
"""
    files = parse_git_diff(diff_text)

    html = assemble_html(files, tmp_path, report_path=tmp_path / ".diffs" / "tokens.html")

    assert "__COMMENT_STORAGE_SCOPE__ __DEFAULT_VIEW__" in html


def test_assemble_html_exposes_comment_management_controls(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path, report_path=tmp_path / ".diffs" / "comments.html")

    assert 'data-clear-comments' in html
    assert 'data-comment-list' in html
    assert 'function updateCommentList(all)' in html
    assert 'function jumpToComment(commentId)' in html
    assert 'function editComment(comment)' in html
    assert 'localStorage.removeItem(STORAGE_KEY)' in html
    assert 'btn-comment btn-edit' in html
