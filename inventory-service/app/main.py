from fastapi import FastAPI, HTTPException
from .db import SessionLocal, engine
from .models import Product, Base
from pydantic import BaseModel
Base.metadata.create_all(bind=engine)

app = FastAPI()

class Product_request_class(BaseModel):
    product_id: str
    quantity: int

@app.get("/list")
def list_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return [{"product_id": p.product_id, "quantity": p.quantity} for p in products]

@app.post("/add")
def add_product(req: Product_request_class):
    db = SessionLocal()
    print("prodotto da aggiungere entrato nella seconda fase con id : ",req.product_id, " quantità: ",req.quantity)
    product = db.query(Product).filter_by(product_id=req.product_id).first()
    if product:
        product.quantity += req.quantity
    else:
        product = Product(product_id=req.product_id, quantity=req.quantity)
        db.add(product)
    db.commit()
    db.close()
    return {"msg": "Prodotto aggiunto o aggiornato"}

@app.post("/reserve")
def reserve_product(req: Product_request_class):
    db = SessionLocal()
    product = db.query(Product).filter_by(product_id=req.product_id).first()
    if not product or product.quantity < req.quantity:
        db.close()
        raise HTTPException(status_code=400, detail="Prodotto non disponibile")
    product.quantity -= req.quantity
    db.commit()
    db.close()
    return {"msg": "Prodotto riservato"}
