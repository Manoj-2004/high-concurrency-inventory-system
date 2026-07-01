from sqlalchemy.orm import Session

from app.models import Product
from app.redis_client import redis_client
from app.schemas import ProductCreate

def create_product(
    product_data: ProductCreate,
    db: Session,
):
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock,
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    redis_client.set(
        f"product:{new_product.id}:stock",
        product_data.stock,
    )
    return new_product

def get_products(db: Session):
    return db.query(Product).all()

def get_product(product_id: int, db: Session):
    return db.query(Product).filter(Product.id == product_id).first()
    