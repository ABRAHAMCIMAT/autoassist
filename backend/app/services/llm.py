from openai import OpenAI


class GroundedGenerator:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = model

    def answer(self, question: str, excerpts: list[str]) -> str | None:
        if not self.client or not excerpts:
            return None
        context = "\n\n".join(f"[{index + 1}] {text}" for index, text in enumerate(excerpts))
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=(
                    "Eres AutoAssist, asistente postventa de DINAMEX. Responde en español, "
                    "de forma breve y únicamente con el contexto proporcionado. No diagnostiques "
                    "fallas ni inventes condiciones. Cita las fuentes como [1], [2]."
                ),
                input=f"Pregunta: {question}\n\nContexto autorizado:\n{context}",
            )
            return response.output_text.strip() or None
        except Exception:
            return None
