# ManPro AI – Home Automation

Phase 1 foundation for the ManPro Home OS: a local-first demo villa with a FastAPI control plane, MQTT bridge contract, generic devices/capabilities, WebSocket live state, and a Next.js dashboard.

## Run

1. Copy `.env.example` to `.env`.
2. Start the stack: `docker compose up --build`.
3. Open `http://localhost:3000`. API documentation: `http://localhost:8000/docs`.

The API seeds **ManPro Demo Villa** automatically. The dashboard controls simulated devices through `POST /api/v1/devices/{id}/commands`; API state broadcasts over WebSocket and is designed to be mirrored by the MQTT gateway.

See [docs/architecture.md](docs/architecture.md) and [docs/phase-1-plan.md](docs/phase-1-plan.md).
