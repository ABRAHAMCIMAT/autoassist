from types import SimpleNamespace

from app.services.llm import GroundedGenerator


class FakeCompletions:
    def __init__(self):
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        message = SimpleNamespace(content="La garantía debe validarse por VIN [1].")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_llama_maverick_grounded_request():
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    generator = GroundedGenerator(
        api_key="test-key",
        model="meta-llama/llama-4-maverick",
        client=client,
    )

    answer = generator.answer("¿Tengo garantía?", ["La cobertura se valida por VIN."])

    assert answer == "La garantía debe validarse por VIN [1]."
    assert completions.request["model"] == "meta-llama/llama-4-maverick"
    assert completions.request["temperature"] == 0.2
    assert "Contexto autorizado" in completions.request["messages"][1]["content"]


def test_generator_without_api_key_is_disabled():
    generator = GroundedGenerator(api_key="", model="meta-llama/llama-4-maverick")
    assert generator.configured is False
    assert generator.answer("pregunta", ["evidencia"]) is None
