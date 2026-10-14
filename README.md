# AutoAssist PoC

PoC local para atención postventa automotriz: garantías, seguimiento de servicio,
gestión de citas y escalamiento A1 → Humano con evidencia completa.

## Inicio rápido

```bash
cp .env.example .env
# Añade OPENAI_API_KEY si deseas respuestas generadas; el modo demo funciona sin ella.
docker compose up --build
```

- Chat: http://localhost:3000
- API: http://localhost:8000/docs
- Salud: http://localhost:8000/health

Con `OPENAI_API_KEY` configurada, las consultas documentales usan el LLM solo
después de recuperar evidencia local. Garantías, órdenes y citas conservan
respuestas deterministas para evitar acciones inventadas.

## Datos de demostración

- VIN: `3D6AA5CG1BG000001`
- Orden: `OT-1001`
- Cita: `CITA-501`

Prueba mensajes como:

- `¿Mi vehículo 3D6AA5CG1BG000001 todavía tiene garantía?`
- `¿Cuál es el estado de la orden OT-1001?`
- `Quiero agendar una cita para el 2026-10-20 a las 10:00.`
- `Quiero hablar con una persona.`

## Diseño

El backend mantiene interfaces independientes para documentos, DMS/CRM y agenda.
Los adaptadores simulados se pueden sustituir posteriormente por herramientas MCP
respaldadas por Nexla sin cambiar el contrato del agente.

## Pruebas

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest
```
