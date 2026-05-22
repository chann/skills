import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PLUGIN_ROOT / "code-review" / "skills" / "diff-viewer" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_diff_report import (  # noqa: E402
    FileDiff,
    assemble_html,
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
