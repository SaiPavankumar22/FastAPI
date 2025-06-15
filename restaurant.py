from davia import Davia
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = Davia()

# ==== MODELS ====

class FoodItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    price: float
    available: bool = True

class TableBooking(BaseModel):
    id: str
    customer_name: str
    table_number: int
    time: str  # ISO datetime string
    guests: int

class OrderItem(BaseModel):
    item_id: str
    quantity: int

class CustomerOrder(BaseModel):
    id: str
    customer_name: str
    table_number: int
    items: List[OrderItem]
    status: str = "pending"  # pending, preparing, served, cancelled

class Bill(BaseModel):
    id: str
    order_id: str
    total_amount: float
    paid: bool = False

class Staff(BaseModel):
    id: str
    name: str
    role: str  # chef, waiter, manager

# ==== DATABASE MOCKS ====
menu_db = []
bookings_db = []
orders_db = []
bills_db = []
staff_db = []

# ==== MENU ROUTES ====

@app.get("/menu", response_model=List[FoodItem])
def get_menu():
    return menu_db

@app.post("/menu", response_model=FoodItem)
def add_food(item: FoodItem):
    item.id = str(uuid4())
    menu_db.append(item)
    return item

@app.put("/menu/{item_id}", response_model=FoodItem)
def update_food(item_id: str, updated_item: FoodItem):
    for i, item in enumerate(menu_db):
        if item.id == item_id:
            updated_item.id = item_id
            menu_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/menu/{item_id}")
def delete_food(item_id: str):
    global menu_db
    menu_db = [item for item in menu_db if item.id != item_id]
    return {"message": "Item deleted"}

# ==== BOOKING ROUTES ====

@app.get("/bookings", response_model=List[TableBooking])
def get_bookings():
    return bookings_db

@app.post("/bookings", response_model=TableBooking)
def create_booking(booking: TableBooking):
    booking.id = str(uuid4())
    bookings_db.append(booking)
    return booking

# ==== ORDER ROUTES ====

@app.get("/orders", response_model=List[CustomerOrder])
def get_orders():
    return orders_db

@app.post("/orders", response_model=CustomerOrder)
def place_order(order: CustomerOrder):
    order.id = str(uuid4())
    orders_db.append(order)
    return order

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: str, status: str):
    for order in orders_db:
        if order.id == order_id:
            order.status = status
            return {"message": "Status updated"}
    raise HTTPException(status_code=404, detail="Order not found")

# ==== BILLING ====

@app.post("/bills", response_model=Bill)
def generate_bill(order_id: str):
    order = next((o for o in orders_db if o.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    total = 0
    for item in order.items:
        menu_item = next((m for m in menu_db if m.id == item.item_id), None)
        if menu_item:
            total += item.quantity * menu_item.price

    bill = Bill(id=str(uuid4()), order_id=order_id, total_amount=total)
    bills_db.append(bill)
    return bill

@app.put("/bills/{bill_id}/pay")
def pay_bill(bill_id: str):
    for bill in bills_db:
        if bill.id == bill_id:
            bill.paid = True
            return {"message": "Payment successful"}
    raise HTTPException(status_code=404, detail="Bill not found")

# ==== STAFF ====

@app.get("/staff", response_model=List[Staff])
def list_staff():
    return staff_db

@app.post("/staff", response_model=Staff)
def add_staff(member: Staff):
    member.id = str(uuid4())
    staff_db.append(member)
    return member

# ==== ROOT ====

@app.get("/")
def home():
    return {"message": "Welcome to the Restaurant Management API!"}
