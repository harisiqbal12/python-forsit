from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Path
from sqlalchemy.orm import Session, Query, joinedload
from app.api.dependencies import get_current_user, get_db
from app.models import inventory
from app.schema.inventory import (
    InventoryCreate,
    InventoryUpdate,
    Inventory as InventorySchema,
    InventoryDetails as InventoryDetailsSchema,
)
from app.models.inventory import Inventory as InventoryModel
from app.models.inventory_history import InventoryHistory as InventoryHistoryModel
import uuid


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"detail": "Not found"}},
)


@router.get("/{product_sku}")
async def get_product_inventory_details(
    product_sku: str, db: Session = Depends(get_db)
):
    inventory = (
        db.query(InventoryModel)
        .join(InventoryModel.product)
        .options(joinedload(InventoryModel.product))
        .filter(InventoryModel.product.has(sku=product_sku))
        .order_by(InventoryModel.created_at.desc())
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404, detail="Inventory not found for this product SKU"
        )

    return {
        "message": "product inventory details retrieved",
        "data": InventoryDetailsSchema.model_validate(inventory, from_attributes=True),
    }


@router.patch("/{inventory_id}")
async def update_inventory(
    req: InventoryUpdate,
    inventory_id: uuid.UUID = Path(..., description="The UUID of the product"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    latest_inventory = (
        db.query(InventoryModel)
        .filter(InventoryModel.id == inventory_id)
        .order_by(InventoryModel.created_at.desc())
        .first()
    )

    if not latest_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    previous_quantity = latest_inventory.quantity
    latest_inventory.quantity = req.quantity
    if req.last_restock_date is not None:
        latest_inventory.last_restock_date = req.last_restock_date

    inventor_history = InventoryHistoryModel(
        inventory_id=latest_inventory.id,
        previous_quantity=previous_quantity,
        new_quantity=req.quantity,
        change_reason=req.change_reason,
        changed_by=user["sub"],
    )

    try:
        db.add(inventor_history)
        db.add(latest_inventory)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to update inventory and history"
        )

    return {
        "message": "inventory updated",
        "data": InventorySchema.model_validate(latest_inventory, from_attributes=True),
    }


@router.post("/")
async def add_inventory(
    req: InventoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):

    latest_inventory = (
        db.query(InventoryModel)
        .filter(InventoryModel.product_id == req.product_id)
        .order_by(InventoryModel.created_at.desc())
        .first()
    )

    if latest_inventory and latest_inventory.quantity > 0:
        raise HTTPException(
            status_code=400,
            detail="Inventory already exists for this product please update instead",
        )

    inventory = InventoryModel(
        product_id=req.product_id,
        quantity=req.quantity,
        last_restock_date=req.last_restock_date,
    )

    inventor_history = InventoryHistoryModel(
        inventory_id=inventory.id,
        previous_quantity=latest_inventory.quantity if latest_inventory else 0,
        new_quantity=req.quantity,
        change_reason=req.change_reason,
        changed_by=user["sub"],
    )

    try:
        db.add(inventory)
        db.flush()
        inventor_history.inventory_id = inventory.id
        db.add(inventor_history)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to add inventory and history"
        )

    return {"message": "Added inventory"}
