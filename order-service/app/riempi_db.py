from models import User, Base
from db import engine, SessionLocal

Base.metadata.create_all(bind=engine)

db = SessionLocal()
db.add_all([
    User(username="admin", password="adminpass", role="admin"),
    User(username="user", password="userpass", role="user")
])
db.commit()
db.close()
