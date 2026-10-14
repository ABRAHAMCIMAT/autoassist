from datetime import date


WARRANTIES = {
    "3D6AA5CG1BG000001": {
        "vehicle": "DINAMEX Cargo 2024",
        "start_date": "2024-02-15",
        "end_date": "2027-02-14",
        "status": "activa",
        "coverage": "Tren motriz y defectos de fabricación",
    }
}

SERVICE_ORDERS = {
    "OT-1001": {
        "vehicle": "DINAMEX Cargo 2024",
        "status": "En diagnóstico",
        "advisor": "Ana Torres",
        "last_update": "2026-10-14T09:30:00Z",
        "next_step": "Confirmar disponibilidad del sensor",
    }
}

APPOINTMENTS: dict[str, dict] = {
    "CITA-501": {
        "date": "2026-10-18",
        "time": "09:00",
        "service": "Mantenimiento preventivo",
        "status": "confirmada",
    }
}


def lookup_warranty(vin: str) -> dict | None:
    return WARRANTIES.get(vin.upper())


def lookup_service_order(order_id: str) -> dict | None:
    return SERVICE_ORDERS.get(order_id.upper())


def create_appointment(day: str, time: str, service: str = "Diagnóstico general") -> dict:
    date.fromisoformat(day)
    appointment_id = f"CITA-{501 + len(APPOINTMENTS)}"
    APPOINTMENTS[appointment_id] = {
        "date": day,
        "time": time,
        "service": service,
        "status": "confirmada",
    }
    return {"id": appointment_id, **APPOINTMENTS[appointment_id]}
