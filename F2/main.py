from fastapi import Depends, FastAPI, HTTPException, status
from models.models import Product
from db.database import session, engine
import db.database_models as db_model
from sqlalchemy.orm import Session

app = FastAPI()

db_model.Base.metadata.create_all(bind=engine)


@app.get("/")
async def hello():
    return {"data": "hello world"}


seed_products = [
    Product(id=1, name="Nord 6", description="good Phone", price=35000, quantity=3),
    Product(id=2, name="laptop", description="good laptop", price=80000, quantity=5),
    Product(id=3, name="charger", description="good charger", price=800, quantity=6),
    Product(id=4, name="dextop", description="good desktop", price=100000, quantity=6),
]


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = session()
    try:
        count = db.query(db_model.Product).count()
        if count == 0:
            for product in seed_products:
                db.add(db_model.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()


init_db()


@app.get("/products", response_model=list[Product])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(db_model.Product).all()


@app.get("/products/{id}", response_model=Product)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_model.Product).filter(db_model.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def add_product(product: Product, db: Session = Depends(get_db)):
    existing = (
        db.query(db_model.Product).filter(db_model.Product.id == product.id).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Product with this id already exists"
        )

    db_product = db_model.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.put("/products/{id}", response_model=Product)
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(db_model.Product).filter(db_model.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.model_dump()
    update_data["id"] = id  # keep path id as source of truth

    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_model.Product).filter(db_model.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
