# Phase 1 checklist

- [x] Monorepo and Docker Compose (PostgreSQL, Redis, Mosquitto, API, web)
- [x] Generic hierarchy, device, capability, state, command, event schema
- [x] Demo Villa seed data and virtual devices
- [x] REST control API and WebSocket state stream
- [x] Mobile-responsive dashboard
- [ ] Add Alembic migrations and authentication before deployment
- [ ] Extract MQTT gateway and virtual-home process; add command acknowledgements/timeouts
- [ ] Add integration tests against MQTT and database containers

Assumptions: Phase 1 is a single trusted demo tenant; a production authentication/RBAC boundary is intentionally deferred, but the schema preserves customer/property scope. MQTT anonymous access is demo-only and must be replaced with TLS credentials per gateway/device.
