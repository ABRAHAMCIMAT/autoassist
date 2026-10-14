import logging

from openai import OpenAI


logger = logging.getLogger(__name__)


class GroundedGenerator:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1",
        temperature: float = 0.2,
        max_tokens: int = 700,
        app_url: str = "http://localhost:3000",
        app_name: str = "AutoAssist DINAMEX PoC",
        client=None,
    ):
        headers = {"HTTP-Referer": app_url, "X-Title": app_name}
        self.client = client or (
            OpenAI(api_key=api_key, base_url=base_url, default_headers=headers) if api_key else None
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def configured(self) -> bool:
        return self.client is not None

    def answer(self, question: str, excerpts: list[str]) -> str | None:
        if not self.client or not excerpts:
            return None
        context = "\n\n".join(f"[{index + 1}] {text}" for index, text in enumerate(excerpts))
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres AutoAssist, asistente postventa de DINAMEX. Responde en español, "
                            "de forma breve y únicamente con el contexto proporcionado. No diagnostiques "
                            "fallas ni inventes condiciones. Cita las fuentes como [1], [2]. Si el contexto "
                            "no permite responder, indica que se requiere revisión humana."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Pregunta: {question}\n\nContexto autorizado:\n{context}",
                    },
                ],
            )
            content = response.choices[0].message.content
            return content.strip() if content else None
        except Exception as error:
            logger.warning("Llama API request failed: %s", type(error).__name__)
            return None
