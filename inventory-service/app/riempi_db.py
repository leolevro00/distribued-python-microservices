from models import Product, Base
from db import engine, SessionLocal

Base.metadata.create_all(bind=engine)

db = SessionLocal()
db.add_all([
    Product(product_id="matita", quantity=10),
    Product(product_id="penna", quantity=30)
])
db.commit()
db.close()
