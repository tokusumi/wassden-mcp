"""Integration tests for spec examples validation."""

import re
import subprocess
from pathlib import Path

import pytest


class TestSpecExamples:
    """Test spec examples in both Japanese and English."""

    @pytest.fixture
    def base_dir(self):
        """Get the base directory of the project."""
        return Path(__file__).parent.parent.parent

    def run_wassden_command(self, base_dir: Path, cmd: list[str]) -> tuple[bool, str]:
        """Run a wassden command and return success status and output."""
        try:
            result = subprocess.run(
                ["uv", "run", "wassden", *cmd], cwd=base_dir, capture_output=True, text=True, timeout=30, check=False
            )
            return result.returncode == 0, result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error: {e}"

    @pytest.mark.parametrize(("lang", "lang_name"), [("ja", "Japanese"), ("en", "English")])
    def test_requirements_validation(self, base_dir, lang, lang_name):
        """Test requirements.md validation for both languages."""
        success, output = self.run_wassden_command(
            base_dir, ["validate-requirements", f"docs/{lang}/spec-example/requirements.md"]
        )
        assert success, f"{lang_name} requirements validation failed: {output}"
        assert "✅" in output, f"{lang_name} requirements validation should show success message"

    @pytest.mark.parametrize(("lang", "lang_name"), [("ja", "Japanese"), ("en", "English")])
    def test_design_validation(self, base_dir, lang, lang_name):
        """Test design.md validation for both languages."""
        success, output = self.run_wassden_command(
            base_dir,
            [
                "validate-design",
                f"docs/{lang}/spec-example/design.md",
                "--requirementsPath",
                f"docs/{lang}/spec-example/requirements.md",
            ],
        )
        assert success, f"{lang_name} design validation failed: {output}"
        assert "✅" in output, f"{lang_name} design validation should show success message"

    @pytest.mark.parametrize(("lang", "lang_name"), [("ja", "Japanese"), ("en", "English")])
    def test_tasks_validation(self, base_dir, lang, lang_name):
        """Test tasks.md validation for both languages."""
        success, output = self.run_wassden_command(base_dir, ["validate-tasks", f"docs/{lang}/spec-example/tasks.md"])
        assert success, f"{lang_name} tasks validation failed: {output}"
        # Note: tasks validation may not show ✅ due to missing design/requirements context

    @pytest.mark.parametrize(("lang", "lang_name"), [("ja", "Japanese"), ("en", "English")])
    def test_traceability_check(self, base_dir, lang, lang_name):
        """Test traceability check for both languages."""
        success, output = self.run_wassden_command(
            base_dir,
            [
                "get-traceability",
                f"docs/{lang}/spec-example/requirements.md",
                "--designPath",
                f"docs/{lang}/spec-example/design.md",
                "--tasksPath",
                f"docs/{lang}/spec-example/tasks.md",
            ],
        )
        assert success, f"{lang_name} traceability check failed: {output}"
        expected_title = "トレーサビリティレポート" if lang == "ja" else "Traceability Report"
        assert expected_title in output, f"{lang_name} should generate traceability report"

    @pytest.mark.parametrize(
        ("input_text", "expected_lang"),
        [
            ("Create a new user authentication system", "English"),
            ("新しいユーザー認証システムを作成したい", "Japanese"),
        ],
    )
    def test_language_detection(self, base_dir, input_text, expected_lang):
        """Test automatic language detection."""
        success, output = self.run_wassden_command(base_dir, ["check-completeness", "--userInput", input_text])
        assert success, f"Language detection failed for {expected_lang}: {output}"

        # Check for language-specific indicators
        if expected_lang == "English":
            assert any(indicator in output for indicator in ["system shall", "English", "Requirements"]), (
                f"English language indicators not found in output: {output[:200]}..."
            )
        else:  # Japanese
            assert any(indicator in output for indicator in ["システムは", "Japanese", "要件", "機能要件"]), (
                f"Japanese language indicators not found in output: {output[:200]}..."
            )


class TestSpecExamplesIntegration:
    """Integration tests that combine multiple validation steps."""

    @pytest.fixture
    def base_dir(self):
        """Get the base directory of the project."""
        return Path(__file__).parent.parent.parent

    def run_wassden_command(self, base_dir: Path, cmd: list[str]) -> tuple[bool, str]:
        """Run a wassden command and return success status and output."""
        try:
            result = subprocess.run(
                ["uv", "run", "wassden", *cmd], cwd=base_dir, capture_output=True, text=True, timeout=30, check=False
            )
            return result.returncode == 0, result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Error: {e}"

    @pytest.mark.parametrize("lang", ["ja", "en"])
    def test_complete_validation_workflow(self, base_dir, lang):
        """Test complete validation workflow for a language."""
        base_path = f"docs/{lang}/spec-example"

        # Step 1: Validate requirements
        success, _ = self.run_wassden_command(base_dir, ["validate-requirements", f"{base_path}/requirements.md"])
        assert success, f"Requirements validation failed for {lang}"

        # Step 2: Validate design
        success, _ = self.run_wassden_command(
            base_dir,
            [
                "validate-design",
                f"{base_path}/design.md",
                "--requirementsPath",
                f"{base_path}/requirements.md",
            ],
        )
        assert success, f"Design validation failed for {lang}"

        # Step 3: Check traceability
        success, output = self.run_wassden_command(
            base_dir,
            [
                "get-traceability",
                f"{base_path}/requirements.md",
                "--designPath",
                f"{base_path}/design.md",
                "--tasksPath",
                f"{base_path}/tasks.md",
            ],
        )
        assert success, f"Traceability check failed for {lang}"

        # Verify traceability coverage
        expected_coverage = "要件カバレッジ: 100.0%" if lang == "ja" else "Requirements coverage: 100.0%"
        assert expected_coverage in output, f"Requirements coverage should be 100% for {lang}"

    def test_cross_language_consistency(self, base_dir):
        """Test that Japanese and English examples have consistent structure."""
        # Get traceability reports for both languages
        ja_success, ja_output = self.run_wassden_command(
            base_dir,
            [
                "get-traceability",
                "docs/ja/spec-example/requirements.md",
                "--designPath",
                "docs/ja/spec-example/design.md",
                "--tasksPath",
                "docs/ja/spec-example/tasks.md",
            ],
        )

        en_success, en_output = self.run_wassden_command(
            base_dir,
            [
                "get-traceability",
                "docs/en/spec-example/requirements.md",
                "--designPath",
                "docs/en/spec-example/design.md",
                "--tasksPath",
                "docs/en/spec-example/tasks.md",
            ],
        )

        assert ja_success, "Japanese traceability check should succeed"
        assert en_success, "English traceability check should succeed"

        # Both should have 100% requirements coverage
        assert "要件カバレッジ: 100.0%" in ja_output, "Japanese should have 100% requirements coverage"
        assert "Requirements coverage: 100.0%" in en_output, "English should have 100% requirements coverage"

        # Extract requirement counts (should be the same)

        ja_req_match = re.search(r"要件数: (\d+)", ja_output)
        en_req_match = re.search(r"要件数: (\d+)", en_output)

        if ja_req_match and en_req_match:
            ja_req_count = int(ja_req_match.group(1))
            en_req_count = int(en_req_match.group(1))
            assert ja_req_count == en_req_count, (
                f"Requirement counts should match: JP={ja_req_count}, EN={en_req_count}"
            )
