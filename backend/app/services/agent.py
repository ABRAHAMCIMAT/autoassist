import re
from dataclasses import dataclass

from .llm import GroundedGenerator
from .mocks import create_appointment, lookup_service_order, lookup_warranty
from .rag import LocalKnowledgeBase


VIN_PATTERN = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b", re.IGNORECASE)
ORDER_PATTERN = re.compile(r"\bOT-?\d+\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
TIME_PATTERN = re.compile(r"\b(?:[01]\d|2[0-3]):[0-5]\d\b")


@dataclass
class AgentResult:
    answer: str
    intent: str
    confidence: float
    escalated: bool = False
    reason: str | None = None
    citations: list[dict] | None = None
    tool_results: list[dict] | None = None


class AutoAssistAgent:
    def __init__(
        self,
        knowledge_base: LocalKnowledgeBase,
        threshold: float = 0.72,
        generator: GroundedGenerator | None = None,
    ):
        self.knowledge_base = knowledge_base
        self.threshold = threshold
        self.generator = generator

    def run(self, message: str) -> AgentResult:
        text = message.lower()
        if any(term in text for term in ("humano", "persona", "asesor", "queja", "reclamo")):
            return AgentResult(
                "Te conectaré con un especialista. Ya preparé el contexto para que no tengas que repetir la información.",
                "escalamiento",
                1.0,
                True,
                "Solicitud explícita o caso sensible",
                [],
                [],
            )

        if any(term in text for term in ("garantía", "garantia", "cobertura")):
            return self._warranty(message)
        if any(term in text for term in ("orden", "servicio", "reparación", "reparacion", "taller")):
            return self._service_order(message)
        if any(term in text for term in ("cita", "agendar", "reservar")):
            return self._appointment(message)

        hits = self.knowledge_base.search(message)
        if hits:
            citations = [{"source": hit.source, "excerpt": hit.excerpt} for hit in hits]
            generated = self.generator.answer(message, [hit.excerpt for hit in hits]) if self.generator else None
            return AgentResult(
                generated or f"Encontré información relacionada: {hits[0].excerpt}",
                "consulta_documental",
                0.76,
                False,
                citations=citations,
                tool_results=[],
            )
        return AgentResult(
            "No tengo evidencia suficiente para responder con seguridad. Te conectaré con un especialista.",
            "desconocido",
            0.30,
            True,
            "Intención no reconocida o evidencia insuficiente",
            [],
            [],
        )

    def _warranty(self, message: str) -> AgentResult:
        match = VIN_PATTERN.search(message)
        if not match:
            return AgentResult("Para consultar la garantía, comparte el VIN de 17 caracteres.", "garantia", 0.86)
        vin = match.group(0).upper()
        warranty = lookup_warranty(vin)
        if not warranty:
            return AgentResult(
                "No encontré el VIN en el sistema de demostración. Lo escalaré para validación manual.",
                "garantia",
                0.55,
                True,
                "VIN sin registro",
                [],
                [{"tool": "lookup_warranty", "vin": vin, "result": None}],
            )
        return AgentResult(
            f"La garantía está {warranty['status']} hasta {warranty['end_date']}. Cobertura: {warranty['coverage']}.",
            "garantia",
            0.96,
            citations=[],
            tool_results=[{"tool": "lookup_warranty", "vin": vin, "result": warranty}],
        )

    def _service_order(self, message: str) -> AgentResult:
        match = ORDER_PATTERN.search(message)
        if not match:
            return AgentResult("Comparte el número de orden, por ejemplo OT-1001.", "seguimiento_servicio", 0.88)
        order_id = match.group(0).upper().replace("OT", "OT-").replace("--", "-")
        order = lookup_service_order(order_id)
        if not order:
            return AgentResult(
                "No encontré esa orden. La enviaré a un especialista para revisión.",
                "seguimiento_servicio",
                0.55,
                True,
                "Orden no localizada",
                [],
                [{"tool": "lookup_service_order", "order_id": order_id, "result": None}],
            )
        return AgentResult(
            f"La orden {order_id} está en estado “{order['status']}”. Siguiente paso: {order['next_step']}.",
            "seguimiento_servicio",
            0.97,
            tool_results=[{"tool": "lookup_service_order", "order_id": order_id, "result": order}],
        )

    def _appointment(self, message: str) -> AgentResult:
        day = DATE_PATTERN.search(message)
        time = TIME_PATTERN.search(message)
        if not day or not time:
            return AgentResult(
                "Indica fecha y hora en formato AAAA-MM-DD y HH:MM para agendar la cita.",
                "gestion_cita",
                0.90,
            )
        appointment = create_appointment(day.group(0), time.group(0))
        return AgentResult(
            f"Cita {appointment['id']} confirmada para el {appointment['date']} a las {appointment['time']}.",
            "gestion_cita",
            0.98,
            tool_results=[{"tool": "create_appointment", "result": appointment}],
        )
