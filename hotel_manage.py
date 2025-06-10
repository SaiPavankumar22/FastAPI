from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session

# Database setup
DATABASE_URL = "sqlite:///./hotel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True)
    type = Column(String)
    is_available = Column(Boolean, default=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    guest_name = Column(String)
    nights = Column(Integer)
    room = relationship("Room")

# Schemas
class RoomCreate(BaseModel):
    number: str
    type: str

class RoomOut(BaseModel):
    id: int
    number: str
    type: str
    is_available: bool
    class Config:
        orm_mode = True

class BookingCreate(BaseModel):
    room_id: int
    guest_name: str
    nights: int

class BookingOut(BaseModel):
    id: int
    room_id: int
    guest_name: str
    nights: int
    class Config:
        orm_mode = True

# App init
app = FastAPI(title="Hotel Management API")
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/rooms/", response_model=RoomOut)
def add_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.get("/rooms/", response_model=List[RoomOut])
def list_rooms(available_only: bool = False, db: Session = Depends(get_db)):
    if available_only:
        return db.query(Room).filter(Room.is_available == True).all()
    return db.query(Room).all()

@app.post("/bookings/", response_model=BookingOut)
def book_room(booking: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == booking.room_id, Room.is_available == True).first()
    if not room:
        raise HTTPException(status_code=400, detail="Room not available or does not exist")
    room.is_available = False
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/", response_model=List[BookingOut])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room.is_available = True
    db.delete(booking)
    db.commit()
    return {"message": "Booking cancelled"}
