from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from db import SessionLocal, init_db
from sqlalchemy.orm import Session
from celery import Celery
import logging

from models import User
import requests
import os


logger = logging.getLogger("order")
celery = Celery("order", broker=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq//"))


app=FastAPI()
INVENTORY_URL = "http://inventory-service:80"
templates=Jinja2Templates(directory="templates")
init_db()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

@app.get("/login",response_class=HTMLResponse)
def login_page(request:Request) :
    return templates.TemplateResponse("login.html", {"request" : request})

@app.post("/login",response_class=HTMLResponse)
def login(request: Request,username: str=Form(...),password: str=Form(...)):
    db=SessionLocal()
    user=get_user_by_username(db, username)
    if user.password == password:
        return templates.TemplateResponse("dashboard.html",{"request": request,"msg":"credenziali inserite con successo","username": username,"role":user.role})
    return templates.TemplateResponse("login.html",{"request": request, "msg": "credenziali non valide"})

@app.post("/buy")
def buy_product(
    username: str = Form(...),
    product_id: str = Form(...),
    quantity: int = Form(...)
):
    # chiamata REST a inventory-service per riservare prodotto
    try:
        response = requests.post(f"{INVENTORY_URL}/reserve", json={
            "product_id": product_id,
            "quantity": quantity
        })
        response.raise_for_status()
        
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Errore durante l'ordine")
    
    # pubblica il task asincrono
    payload = {"user": username, "product_id": product_id, "quantity": quantity}
    celery.send_task("notify.send_purchase", args=[payload])

    return {"status": "success", "message": "Ordine effettuato"}

@app.get("/inventory/view")
def view_inventory():
    try:
        response = requests.get(f"{INVENTORY_URL}/list")
        response.raise_for_status()
        return response.json()
    except:
        raise HTTPException(status_code=500, detail="Errore inventory-service")
    

@app.post("/inventory/add")
def add_product(product_id: str = Form(...), quantity: int = Form(...)):
    print("prodotto da aggiungere: ",product_id, " quantità: ",quantity)
    response = requests.post(f"{INVENTORY_URL}/add", json={
        "product_id": product_id,
        "quantity": quantity
    })
    return {"msg": "Prodotto aggiunto"}