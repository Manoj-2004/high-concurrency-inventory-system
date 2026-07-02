from app.database import SessionLocal
from app.models import Order, OrderItem, OrderStatus, Product
from sqlalchemy.exc import IntegrityError
from app.logging_config import logger

def process_purchase_event(event: dict):
    db = SessionLocal()

    try:
        event_id = event["event_id"]
        user_id = event["user_id"]
        product_id = event["product_id"]
        quantity = event["quantity"]

        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            logger.warning(f"Product {product_id} not found")
            return

        total_amount = product.price * quantity

        new_order = Order(
            event_id=event_id,
            user_id=user_id,
            status=OrderStatus.CONFIRMED.value,
            total_amount=total_amount,
        )

        db.add(new_order)
        db.flush()

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
        )

        db.add(order_item)

        product.stock = product.stock - quantity

        db.commit()

        logger.info(f"Order {new_order.id} created successfully")

    except IntegrityError:
        db.rollback()
        logger.info(
            f"Event {event.get('event_id')} already processed by DB constraint. Skipping."
        )
        return

    except Exception as error:
        db.rollback()
        logger.exception(f"Failed to process purchase event: {error}")
        raise
    
    finally:
        db.close()