from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import random
import string

from app.api.dependencies import get_current_user, get_db
from app.core.kafka_producer import send_order_event, send_sales_event
from app.schema.orders import OrderCreate, Order as OrderSchema
from app.models.orders import Order as OrderModel
from app.models.orders_items import OrderItem as OrderItemModel
from app.models.product import Product as ProductModel
from app.models.inventory import Inventory as InventoryModel
from app.models.inventory_history import (
    InventoryHistory as InventoryHistoryModel,
)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"detail": "Not found"}},
)


def generate_order_number() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_part}-{random_part}"


@router.post("/")
async def place_order(
    background_task: BackgroundTasks,
    req: OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    order_number = generate_order_number()
    print("36")

    product_ids = [item.product_id for item in req.items]
    products = {
        p.id: p
        for p in db.query(ProductModel).filter(ProductModel.id.in_(product_ids)).all()
    }

    inventories = {
        inv.product_id: inv
        for inv in db.query(InventoryModel)
        .filter(InventoryModel.product_id.in_(product_ids))
        .all()
    }

    for item in req.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {item.product_id} does not exist",
            )
        if product.status != "ACTIVE":
            raise HTTPException(
                status_code=400,
                detail=f"Product with id {item.product_id} is not active",
            )

        inventory = inventories.get(item.product_id)
        available_qty = inventory.quantity if inventory else 0
        if available_qty < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough inventory for product id {item.product_id}. Requested: {item.quantity}, Available: {available_qty}",
            )

    total_amount = sum(
        products[item.product_id].price * item.quantity for item in req.items
    )
    tax_amount = 1.2
    shipping_amount = 0.99 * len(req.items)
    discount_amount = 0

    order = OrderModel(
        order_number=order_number,
        channel_id=req.channel_id,
        order_date=req.order_date or datetime.utcnow(),
        total_amount=total_amount,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        discount_amount=discount_amount,
        status=req.status,
        customer_name=req.customer_name,
        customer_email=req.customer_email,
        shipping_address=req.shipping_address,
        billing_address=req.billing_address,
    )

    try:
        db.add(order)
        db.flush()

        for item in req.items:
            product = products[item.product_id]
            order_item = OrderItemModel(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=product.price * item.quantity,
            )
            db.add(order_item)

            inventory = inventories.get(item.product_id)
            if inventory:
                previous_quantity = inventory.quantity
                inventory.quantity -= item.quantity
                db.add(inventory)

                inventory_history = InventoryHistoryModel(
                    inventory_id=inventory.id,
                    previous_quantity=previous_quantity,
                    new_quantity=inventory.quantity,
                    change_reason="Order placed",
                    changed_by=user["sub"],
                )
                db.add(inventory_history)

        db.commit()
        db.refresh(order)
        background_task.add_task(
            send_order_event,
            OrderSchema.model_validate(order, from_attributes=True).model_dump(),
        )

        for item in req.items:
            product = products[item.product_id]
            for p in range(item.quantity):
                sales_event = {
                    "order_id": str(order.id),
                    "order_item_id": str(order_item.id),
                    "product_id": str(item.product_id),
                    "category_id": (
                        str(product.category_id) if product.category_id else None
                    ),
                    "channel_id": str(order.channel_id),
                    "sale_date": datetime.now().isoformat(),
                    "amount": float(product.price),
                }
                background_task.add_task(send_sales_event, sales_event)
                print("will publish: ", p)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

    return {
        "message": "order placed successfully",
        "data": OrderSchema.model_validate(order, from_attributes=True),
    }
