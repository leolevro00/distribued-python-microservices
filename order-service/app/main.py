from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.db import SessionLocal, init_db
from sqlalchemy.orm import Session

from app.models import User
import requests
import os

app=FastAPI()

templates=Jinja2Templates(directory="app/templates")
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
        return {"status": "success", "message": "Ordine effettuato"}
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Errore durante l'ordine")
    
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
    response = requests.post(f"{INVENTORY_URL}/add", json={
        "product_id": product_id,
        "quantity": quantity
    })
    return {"msg": "Prodotto aggiunto"}