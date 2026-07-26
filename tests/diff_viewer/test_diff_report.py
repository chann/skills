import sys
from datetime import datetime, timezone
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PLUGIN_ROOT / "code-review" / "skills" / "diff-viewer" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_diff_report import (  # noqa: E402
    FileDiff,
    LANGUAGES,
    assemble_html,
    build_comment_storage_scope,
    build_highlight_seeds,
    detect_language,
    parse_args,
    parse_git_diff,
    render_body,
    render_highlight_seeds,
    render_file_diff,
    render_language_control,
    render_nav,
    render_split_table,
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


def test_render_file_diff_marks_inline_word_diff_ranges_in_both_views():
    diff_text = """diff --git a/src/hello.py b/src/hello.py
index 1111111..2222222 100644
--- a/src/hello.py
+++ b/src/hello.py
@@ -1 +1 @@
-return "Hello, " + name
+return f"Hello, {name}"
"""
    files = parse_git_diff(diff_text)

    html = render_file_diff(files[0], index=0)

    assert html.count('data-inline-diff-kind="del"') == 2
    assert html.count('data-inline-diff-kind="add"') == 2
    assert html.count("data-inline-diff-ranges=") == 4


def test_split_table_styles_additions_and_deletions_per_cell():
    diff_text = """diff --git a/src/hello.py b/src/hello.py
index 1111111..2222222 100644
--- a/src/hello.py
+++ b/src/hello.py
@@ -1 +1 @@
-return "Hello, " + name
+return f"Hello, {name}"
"""
    files = parse_git_diff(diff_text)

    html = render_split_table(files[0], language="python", file_index=0)

    assert '<tr class="split-row line-del line-add">' not in html
    assert '<td class="line-no line-del">1</td><td class="code-line line-del">' in html
    assert '<td class="line-no line-add">1</td><td class="code-line line-add">' in html


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
    assert "function applyInlineDiff" in html
    assert ".inline-diff-add" in html
    assert ".inline-diff-del" in html


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


def test_supported_languages_are_korean_and_english():
    assert LANGUAGES == ("en", "ko")


def test_parse_args_accepts_a_language_choice():
    assert parse_args([]).language == "auto"
    assert parse_args(["--language", "ko"]).language == "ko"
    assert parse_args(["--language", "en"]).language == "en"


def test_language_control_is_a_labelled_group_of_pressable_buttons():
    control = render_language_control()

    assert 'role="group"' in control
    assert 'data-i18n-label="language"' in control
    for code in LANGUAGES:
        assert f'data-set-lang="{code}"' in control
    assert control.count('type="button"') == len(LANGUAGES)
    assert "한국어" in control
    assert "English" in control


def test_assemble_html_embeds_language_defaults_and_control(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    assert "__DEFAULT_LANG__" not in html
    assert "__LANG_CODES__" not in html
    assert "__LANGUAGE_CONTROL__" not in html
    assert 'data-set-lang="ko"' in html
    assert 'data-set-lang="en"' in html
    assert '"en", "ko"' in html or '"en","ko"' in html


def test_assemble_html_honors_the_requested_default_language(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))

    korean = assemble_html(files, tmp_path, default_language="ko")
    auto = assemble_html(files, tmp_path)

    assert 'lang: "ko"' in korean
    assert 'lang: "auto"' in auto


def test_file_status_carries_a_translation_key(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = render_file_diff(files[0], index=0)

    assert 'data-i18n="statusModified"' in html
    assert ">modified<" in html


def test_every_file_status_maps_to_a_translation_key():
    diff_text = """diff --git a/added.py b/added.py
new file mode 100644
--- /dev/null
+++ b/added.py
@@ -0,0 +1 @@
+x = 1
diff --git a/removed.py b/removed.py
deleted file mode 100644
--- a/removed.py
+++ /dev/null
@@ -1 +0,0 @@
-y = 2
"""
    files = parse_git_diff(diff_text)

    html = render_body(files)

    assert 'data-i18n="statusAdded"' in html
    assert 'data-i18n="statusDeleted"' in html


def test_empty_states_carry_translation_keys():
    assert 'data-i18n="noChanges"' in render_nav([])
    body = render_body([])
    assert 'data-i18n="emptyTitle"' in body
    assert 'data-i18n="emptyBody"' in body


def test_summary_captions_carry_translation_keys(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    for key in ("filesChanged", "additions", "deletions"):
        assert f'data-i18n="{key}"' in html


def test_runtime_declares_korean_and_english_message_tables(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    assert "const I18N = {" in html
    assert "function setLang(lang)" in html
    assert 'localStorage.setItem("diff-viewer:lang"' in html
    for key in (
        "filesChanged",
        "additions",
        "deletions",
        "comments",
        "noComments",
        "copyMarkdown",
        "clearComments",
        "statusModified",
        "statusRenamed",
        "placeholder",
        "save",
        "cancel",
        "edit",
        "delete",
    ):
        assert f"{key}:" in html
    for korean in ("변경된 파일", "코멘트", "마크다운 복사", "저장", "취소"):
        assert korean in html


def test_runtime_localizes_labels_placeholders_and_document_language(
    load_fixture,
    tmp_path,
):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    assert "[data-i18n]" in html
    assert "[data-i18n-label]" in html
    assert "[data-i18n-placeholder]" in html
    # setLang persists the *resolved* code, never the literal "auto" it may receive.
    assert 'setAttribute("lang", activeLang)' in html
    assert 'localStorage.setItem("diff-viewer:lang", activeLang)' in html


def test_changing_language_rerenders_threads_and_dismisses_the_open_editor(
    load_fixture,
    tmp_path,
):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    assert "window.renderDiffComments = () => {" in html
    assert "closeInput();" in html
    assert 'if (typeof window.renderDiffComments === "function") window.renderDiffComments();' in html


def test_line_range_labels_are_language_specific(load_fixture, tmp_path):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    assert '"Line " + n' in html
    assert '"번째 줄"' in html
    assert "function formatRange(startLine, endLine)" in html
    assert html.count("function formatRange(") == 1


def test_exported_markdown_headings_follow_the_active_language(
    load_fixture,
    tmp_path,
):
    files = parse_git_diff(load_fixture("simple.diff"))

    html = assemble_html(files, tmp_path)

    assert '"# Code Review Feedback\\n\\n"' not in html
    assert 't("feedbackTitle")' in html
    assert "feedbackTitle:" in html
    assert "리뷰 피드백" in html


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
