from pathlib import Path

from tools.edunova.agents.evidence import TaskEvidenceCollector


def test_collector_reads_explicit_file(tmp_path: Path):
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 42\n", encoding="utf-8")

    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect(
        "Analyse src/example.py"
    )

    assert len(evidence) == 1
    assert evidence[0].path == "src/example.py"
    assert evidence[0].exists is True
    assert evidence[0].content.replace("\r\n", "\n") == "VALUE = 42\n"


def test_collector_reports_unknown_file(tmp_path: Path):
    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect(
        "Analyse src/missing.py"
    )

    assert len(evidence) == 1
    assert evidence[0].path == "src/missing.py"
    assert evidence[0].exists is False


def test_collector_does_not_infer_from_file_name(tmp_path: Path):
    target = tmp_path / "tests" / "test_sqlite_repository.py"
    target.parent.mkdir(parents=True)
    target.write_text("def test_repository():\n    pass\n", encoding="utf-8")

    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect(
        "Quelle base de données est utilisée ?"
    )

    assert evidence == ()


def test_collector_limits_large_files(tmp_path: Path):
    target = tmp_path / "src" / "large.py"
    target.parent.mkdir(parents=True)
    target.write_text("x" * 100, encoding="utf-8")

    collector = TaskEvidenceCollector(tmp_path, max_file_size=20)

    evidence = collector.collect(
        "Analyse src/large.py"
    )

    assert evidence[0].exists is True
    assert "CONTENT OMITTED" in evidence[0].content


def test_prompt_section_marks_evidence_as_direct():
    collector = TaskEvidenceCollector(Path("."))

    section = collector.build_prompt_section(
        (
            type(
                "Evidence",
                (),
                {
                    "path": "src/example.py",
                    "exists": True,
                    "content": "VALUE = 42",
                    "start_line": 1,
                    "end_line": 1,
                },
            )(),
        )
    )

    assert "EXPLICIT FILE EVIDENCE:" in section
    assert "FILE: src/example.py" in section
    assert "VALUE = 42" in section

def test_collector_reads_multiple_explicit_files_with_line_ranges(tmp_path: Path):
    first = tmp_path / "src" / "first.py"
    second = tmp_path / "tools" / "second.py"

    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)

    first.write_text(
        "line1\nline2\nline3\n",
        encoding="utf-8",
    )
    second.write_text(
        "only_line\n",
        encoding="utf-8",
    )

    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect(
        "Analyse src/first.py et tools/second.py"
    )

    assert len(evidence) == 2

    assert evidence[0].path == "src/first.py"
    assert evidence[0].exists is True
    assert evidence[0].start_line == 1
    assert evidence[0].end_line == 3

    assert evidence[1].path == "tools/second.py"
    assert evidence[1].exists is True
    assert evidence[1].start_line == 1
    assert evidence[1].end_line == 1


def test_collector_does_not_read_unreferenced_files(tmp_path: Path):
    target = tmp_path / "src" / "secret.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "SECRET = 'must not be collected'\n",
        encoding="utf-8",
    )

    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect(
        "Analyse le projet sans référencer le fichier"
    )

    assert evidence == ()


def test_collector_blocks_path_traversal_outside_project_root(tmp_path: Path):
    secret = tmp_path / ".env"
    secret.write_text("TOKEN=must-not-leak\n", encoding="utf-8")
    source = tmp_path / "src"
    source.mkdir()

    collector = TaskEvidenceCollector(source)

    evidence = collector.collect("Analyse src/../../.env")

    assert len(evidence) == 1
    assert evidence[0].exists is False
    assert "CONTENT BLOCKED" in evidence[0].content
    assert "must-not-leak" not in evidence[0].content


def test_collector_blocks_sensitive_file_types_inside_project(tmp_path: Path):
    target = tmp_path / "src" / "credentials.pem"
    target.parent.mkdir(parents=True)
    target.write_text("private material", encoding="utf-8")

    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect("Analyse src/credentials.pem")

    assert len(evidence) == 1
    assert evidence[0].exists is False
    assert "CONTENT BLOCKED" in evidence[0].content
    assert "private material" not in evidence[0].content


def test_collector_prompt_contains_line_provenance(tmp_path: Path):
    target = tmp_path / "src" / "example.py"
    target.parent.mkdir(parents=True)

    target.write_text(
        "A = 1\nB = 2\n",
        encoding="utf-8",
    )

    collector = TaskEvidenceCollector(tmp_path)

    evidence = collector.collect(
        "Analyse src/example.py"
    )

    section = collector.build_prompt_section(evidence)

    assert "FILE: src/example.py" in section
    assert "EXISTS: yes" in section
    assert "LINES: 1-2" in section
    assert "A = 1" in section
    assert "B = 2" in section
