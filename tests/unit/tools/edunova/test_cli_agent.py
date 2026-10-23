from tools.edunova import cli
from tools.edunova.cli import main


def test_main_passes_agent_task_to_dispatcher(monkeypatch):
    captured = {}

    class FakeBootstrap:
        def __init__(self, process_runner=None):
            self.dispatcher = self

        def dispatch(self, name, args=()):
            captured["name"] = name
            captured["args"] = args

            class Result:
                exit_code = 0

            return Result()

    monkeypatch.setattr(cli, "CliBootstrap", FakeBootstrap)

    result = main(["agent-orchestrated", "analyse EduNova"])

    assert result == 0
    assert captured["name"] == "agent-orchestrated"
    assert captured["args"] == ["analyse EduNova"]
