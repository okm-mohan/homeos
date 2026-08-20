from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, JSON, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./manpro.db")
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase): pass
class Customer(Base):
    __tablename__ = "customers"; id: Mapped[str] = mapped_column(String, primary_key=True); name: Mapped[str] = mapped_column(String)
class Property(Base):
    __tablename__ = "properties"; id: Mapped[str] = mapped_column(String, primary_key=True); customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id")); name: Mapped[str] = mapped_column(String)
class Building(Base):
    __tablename__ = "buildings"; id: Mapped[str] = mapped_column(String, primary_key=True); property_id: Mapped[str] = mapped_column(ForeignKey("properties.id")); name: Mapped[str] = mapped_column(String)
class Floor(Base):
    __tablename__ = "floors"; id: Mapped[str] = mapped_column(String, primary_key=True); building_id: Mapped[str] = mapped_column(ForeignKey("buildings.id")); name: Mapped[str] = mapped_column(String)
class Room(Base):
    __tablename__ = "rooms"; id: Mapped[str] = mapped_column(String, primary_key=True); floor_id: Mapped[str] = mapped_column(ForeignKey("floors.id")); name: Mapped[str] = mapped_column(String); icon: Mapped[str] = mapped_column(String, default="home")
class DeviceType(Base):
    __tablename__ = "device_types"; id: Mapped[str] = mapped_column(String, primary_key=True); name: Mapped[str] = mapped_column(String); category: Mapped[str] = mapped_column(String)
class Device(Base):
    __tablename__ = "devices"; id: Mapped[str] = mapped_column(String, primary_key=True); room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id")); device_type_id: Mapped[str] = mapped_column(ForeignKey("device_types.id")); name: Mapped[str] = mapped_column(String); online: Mapped[bool] = mapped_column(default=True)
class CapabilityState(Base):
    __tablename__ = "capability_states"; id: Mapped[str] = mapped_column(String, primary_key=True); device_id: Mapped[str] = mapped_column(ForeignKey("devices.id")); capability: Mapped[str] = mapped_column(String); value: Mapped[Any] = mapped_column(JSON); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
class DeviceCommand(Base):
    __tablename__ = "device_commands"; id: Mapped[str] = mapped_column(String, primary_key=True); device_id: Mapped[str] = mapped_column(ForeignKey("devices.id")); capability: Mapped[str] = mapped_column(String); value: Mapped[Any] = mapped_column(JSON); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Command(BaseModel): capability: str; value: Any
class Hub:
    clients: list[WebSocket] = []
    async def broadcast(self, payload: dict):
        for client in self.clients.copy():
            try: await client.send_json(payload)
            except Exception: self.clients.remove(client)
hub = Hub()
app = FastAPI(title="ManPro Home OS API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
def seed():
    with Session(engine) as s:
        if s.scalar(select(Customer.id).limit(1)): return
        c=Customer(id="demo-customer",name="ManPro Demo"); p=Property(id="demo-villa",customer_id=c.id,name="ManPro Demo Villa"); b=Building(id="main-house",property_id=p.id,name="Main House")
        floors=[Floor(id="ground",building_id=b.id,name="Ground Floor"),Floor(id="first",building_id=b.id,name="First Floor")]
        rooms=[Room(id="living",floor_id="ground",name="Living Room",icon="sofa"),Room(id="kitchen",floor_id="ground",name="Kitchen",icon="utensils"),Room(id="master",floor_id="first",name="Master Bedroom",icon="bed"),Room(id="garden",floor_id="ground",name="Garden",icon="tree")]
        types=[DeviceType(id="light",name="Light",category="Electrical"),DeviceType(id="fan",name="Fan",category="Electrical"),DeviceType(id="climate",name="Air Conditioner",category="Climate"),DeviceType(id="curtain",name="Curtain",category="Curtains"),DeviceType(id="sensor",name="Sensor",category="Safety")]
        spec=[("living-light","living","light","Ceiling Light",{"power":False,"brightness":60}),("living-fan","living","fan","Ceiling Fan",{"power":False,"speed":2}),("living-ac","living","climate","Living Room AC",{"power":False,"temperature":25}),("living-curtain","living","curtain","Curtains",{"position":20}),("kitchen-light","kitchen","light","Kitchen Light",{"power":False,"brightness":80}),("kitchen-gas","kitchen","sensor","Gas Sensor",{"gas":False}),("master-ac","master","climate","Master AC",{"power":False,"temperature":24}),("garden-light","garden","light","Garden Light",{"power":False})]
        s.add_all([c,p,b,*floors,*rooms,*types])
        for did,rid,tid,name,states in spec:
            s.add(Device(id=did,room_id=rid,device_type_id=tid,name=name))
            for cap,value in states.items(): s.add(CapabilityState(id=uid(),device_id=did,capability=cap,value=value,updated_at=now()))
        s.commit()
@app.on_event("startup")
def startup(): Base.metadata.create_all(engine); seed()
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/api/v1/dashboard")
def dashboard():
    with Session(engine) as s:
        devices=s.scalars(select(Device)).all(); states=s.scalars(select(CapabilityState)).all(); rooms={r.id:r.name for r in s.scalars(select(Room)).all()}; by_device={}
        for state in states: by_device.setdefault(state.device_id,{})[state.capability]=state.value
        return {"property":"ManPro Demo Villa","home_state":"HOME","devices":[{"id":d.id,"name":d.name,"room":rooms[d.room_id],"online":d.online,"capabilities":by_device.get(d.id,{})} for d in devices]}
@app.post("/api/v1/devices/{device_id}/commands")
async def command(device_id: str, data: Command):
    with Session(engine) as s:
        device=s.get(Device,device_id)
        if not device: raise HTTPException(404,"Device not found")
        state=s.scalar(select(CapabilityState).where(CapabilityState.device_id==device_id,CapabilityState.capability==data.capability))
        if state: state.value=data.value; state.updated_at=now()
        else: s.add(CapabilityState(id=uid(),device_id=device_id,capability=data.capability,value=data.value,updated_at=now()))
        s.add(DeviceCommand(id=uid(),device_id=device_id,capability=data.capability,value=data.value,created_at=now())); s.commit()
    event={"type":"device.state","device_id":device_id,"capability":data.capability,"value":data.value,"source":"simulator"}
    await hub.broadcast(event); return {"accepted":True,"mqtt_topic":f"manpro/v1/demo-villa/{device.room_id}/{device_id}/command",**event}
@app.websocket("/ws")
async def ws(socket: WebSocket):
    await socket.accept(); hub.clients.append(socket)
    try:
        while True: await socket.receive_text()
    except WebSocketDisconnect: hub.clients.remove(socket)
