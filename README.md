# AutoAssist PoC

PoC local para atención postventa automotriz: garantías, seguimiento de servicio,
gestión de citas y escalamiento A1 → Humano con evidencia completa.

## Inicio rápido

```bash
cp .env.example .env
# Añade tu LLM_API_KEY de OpenRouter; el modo demo funciona sin ella.
docker compose up --build
```

- Chat: http://localhost:3000
- API: http://localhost:8000/docs
- Salud: http://localhost:8000/health

## Llama 4 Maverick mediante API

El PoC usa por defecto `meta-llama/llama-4-maverick` mediante la API compatible
con OpenAI de OpenRouter. Crea una clave en <https://openrouter.ai/keys> y colócala
solo en tu archivo local `.env`:

```dotenv
LLM_API_KEY=tu_clave
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=meta-llama/llama-4-maverick
```

Las consultas documentales usan Maverick únicamente después de recuperar
evidencia local. Garantías, órdenes y citas conservan respuestas deterministas
para evitar acciones inventadas. Si la API falla, el agente usa una respuesta
segura basada en el fragmento recuperado; nunca envía la clave al navegador.

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
