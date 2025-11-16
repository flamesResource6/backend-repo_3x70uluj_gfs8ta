import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="St. Lucia Tours & Rentals API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Pydantic Schemas (for request/response) ----------
class Tour(BaseModel):
    title: str = Field(..., description="Tour name")
    description: str = Field(..., description="What guests will experience")
    price: float = Field(..., ge=0)
    duration_hours: int = Field(..., ge=1)
    location: str = Field(..., description="Where the tour starts")
    image_url: Optional[str] = None
    featured: bool = False

class Vehicle(BaseModel):
    name: str
    type: str = Field(..., description="Car, SUV, Jeep, Scooter, Boat")
    seats: int = Field(..., ge=1)
    price_per_day: float = Field(..., ge=0)
    transmission: str = Field(..., description="Automatic/Manual")
    image_url: Optional[str] = None
    available: bool = True

class Booking(BaseModel):
    kind: str = Field(..., description="tour or vehicle")
    item_id: str
    name: str
    email: str
    phone: Optional[str] = None
    date: str
    notes: Optional[str] = None

# ---------- Helpers ----------
def to_public(doc: dict):
    d = doc.copy()
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "St. Lucia Tours & Rentals Backend running"}

@app.get("/test")
def test_database():
    response = {"backend": "✅ Running", "database": "❌ Not Available"}
    try:
        if db is not None:
            response["database"] = "✅ Connected"
            response["collections"] = db.list_collection_names()
    except Exception as e:
        response["database"] = f"⚠️ {str(e)[:80]}"
    return response

# Seed example content if empty
@app.post("/seed")
def seed_data():
    try:
        created = {"tours": 0, "vehicles": 0}
        if db["tour"].count_documents({}) == 0:
            samples: List[Tour] = [
                Tour(title="Gros Piton Hike", description="Guided hike up the iconic Pitons with breathtaking views.", price=95, duration_hours=5, location="Soufrière", image_url="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee", featured=True),
                Tour(title="Sulphur Springs & Mud Bath", description="Revitalizing mud baths at the Caribbean's only drive-in volcano.", price=60, duration_hours=2, location="Soufrière", image_url="https://images.unsplash.com/photo-1500375592092-40eb2168fd21"),
                Tour(title="Rainforest Zipline Adventure", description="High-flying zipline through lush rainforest canopies.", price=120, duration_hours=3, location="Babonneau", image_url="https://images.unsplash.com/photo-1511497584788-876760111969")
            ]
            for t in samples:
                create_document("tour", t)
                created["tours"] += 1
        if db["vehicle"].count_documents({}) == 0:
            vehicles: List[Vehicle] = [
                Vehicle(name="Suzuki Jimny", type="Jeep", seats=4, price_per_day=65, transmission="Automatic", image_url="https://images.unsplash.com/photo-1552519507-da3b142c6e3d"),
                Vehicle(name="Toyota Yaris", type="Car", seats=5, price_per_day=45, transmission="Automatic", image_url="https://images.unsplash.com/photo-1549924231-f129b911e442"),
                Vehicle(name="Nissan X-Trail", type="SUV", seats=5, price_per_day=80, transmission="Automatic", image_url="https://images.unsplash.com/photo-1511919884226-fd3cad34687c")
            ]
            for v in vehicles:
                create_document("vehicle", v)
                created["vehicles"] += 1
        return {"status": "ok", "created": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Public listing endpoints
@app.get("/tours")
def list_tours():
    items = get_documents("tour")
    return [to_public(i) for i in items]

@app.get("/vehicles")
def list_vehicles():
    items = get_documents("vehicle")
    return [to_public(i) for i in items]

# Booking endpoint (collect leads)
@app.post("/book")
def book_item(data: Booking):
    try:
        if data.kind not in ("tour", "vehicle"):
            raise HTTPException(status_code=400, detail="Invalid kind")
        inserted_id = create_document("booking", data)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
