# Phase 1 architecture

ManPro is a local-first modular monorepo. Phase 1 runs a Home Hub-compatible stack locally: the API owns metadata and authorization boundaries; MQTT is the device/event transport; the simulator behaves as a device adapter; WebSockets project authoritative state to clients.

```
Dashboard -> REST command -> API -> MQTT command topic -> adapter/simulator
                                               -> MQTT state topic -> API -> WebSocket -> Dashboard
```

## Core model

`Customer > Property > Building > Floor > Room/Zone > Device > Capability` is relational. A device type describes reusable capability definitions, while a device holds capability state as a typed JSON value. Commands and events are append-only audit records. This avoids hard-coding lights, fans, or protocol details.

## MQTT convention

`manpro/v1/{property_id}/{room_id}/{device_id}/{kind}` where `kind` is `command`, `state`, `telemetry`, `availability`, or `event`. Payloads include `message_id`, `timestamp`, `source`, and `correlation_id`; commands require a state acknowledgement before timeout. Device adapters own protocol translation and validate against the unified capability contract.

## Service boundaries

* `services/api`: identity boundary, property/device API, state projection, WebSocket gateway.
* `services/mqtt-gateway`: future durable MQTT consumer/adapter registry (the Phase 1 API exposes its contract).
* `simulator/virtual-home`: future simulator process; Phase 1 seed and command endpoint supply an in-process demo adapter.
* `apps/web`: responsive operator UI only, with no hardware-specific logic.

PostgreSQL is durable system-of-record; Redis is reserved for presence, WebSocket fanout, rate limiting, and state cache. Critical automations will remain Hub-local in Phase 2.
