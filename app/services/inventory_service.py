from sqlalchemy.orm import Session

from app.models import Product
from app.redis_client import redis_client


def sync_redis_stock_from_db(db: Session):
    products = db.query(Product).all()

    for product in products:
        redis_client.set(
            f"product:{product.id}:stock",
            product.stock,
        )

    return {
        "message": "Redis stock synced from PostgreSQL",
        "products_synced": len(products),
    }