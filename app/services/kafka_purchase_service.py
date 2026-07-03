from app.database import SessionLocal
from app.models import Order, OrderItem, OrderStatus, Product, CartItem, Address
from sqlalchemy.exc import IntegrityError
from app.logging_config import logger
from app.kafka.producer import publish_dlq_event

def process_purchase_event(event: dict):
    db = SessionLocal()

    try:
        event_id = event["event_id"]
        user_id = event["user_id"]
        items = event["items"]
        address_id = event["address_id"]
        
        address = (
            db.query(Address)
            .filter(Address.id == address_id, Address.user_id == user_id)
            .first()
        )

        if not address:
            logger.warning(f"Address {address_id} not found. Sending to DLQ.")
            publish_dlq_event({
                "original_event": event,
                "error": f"Address {address_id} not found",
                "reason": "NON_RETRYABLE",
            })
            return
        
        
        products_to_order = []
        total_amount = 0

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product = db.query(Product).filter(Product.id == product_id).first()

            if not product:
                logger.warning(f"Product {product_id} not found. Sending to DLQ.")
                publish_dlq_event({
                    "original_event": event,
                    "error": f"Product {product_id} not found",
                    "reason": "NON_RETRYABLE",
                })
                return

            if product.stock < quantity:
                logger.warning(f"Insufficient stock for product {product_id}. Sending to DLQ.")
                publish_dlq_event({
                    "original_event": event,
                    "error": f"Insufficient stock for product {product_id}",
                    "reason": "NON_RETRYABLE",
                })
                return

            products_to_order.append((product, quantity))
            total_amount += product.price * quantity

        new_order = Order(
            event_id=event_id,
            user_id=user_id,
            status=OrderStatus.CONFIRMED.value,
            total_amount=total_amount,
            shipping_full_name=address.full_name,
            shipping_phone=address.phone,
            shipping_address_line_1=address.address_line_1,
            shipping_address_line_2=address.address_line_2,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,
        )

        db.add(new_order)
        db.flush()

        for product, quantity in products_to_order:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price,
            )

            db.add(order_item)
            product.stock = product.stock - quantity

        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()

        logger.info(f"Order {new_order.id} created successfully with {len(items)} items")

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