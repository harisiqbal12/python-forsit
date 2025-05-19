from typing import Callable, Optional
from fastapi import APIRouter, HTTPException, Depends, Path
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, Query
from sqlalchemy.orm import joinedload
from typing import List

from app.api.dependencies import get_current_user, get_db
from app.models.product import Product as ProductModel
from app.models.category import Category as CategoryModel

from app.schema.product import (
    ProductCreate,
    Product as ProductSchema,
    ProductSecondary as ProductSecondarySchema,
    ProductUpdate as ProductUpdateSchema,
)


router = APIRouter(
    prefix="/product",
    tags=["product"],
    responses={404: {"detail": "Not found"}},
)


def apply_search(query: Query, search: Optional[str]) -> Query:
    if search:
        search_pattern = f"%{search}%"
        return query.filter(
            (ProductModel.sku.ilike(search_pattern))
            | (ProductModel.name.ilike(search_pattern))
            | (ProductModel.description.ilike(search_pattern))
        )
    return query


def apply_filter_category(query: Query, category_id: Optional[str]) -> Query:
    if category_id:
        return query.filter(ProductModel.category_id == category_id)
    return query


def apply_filter_created_by(query: Query, created_by: Optional[str]) -> Query:
    if created_by:
        return query.filter(ProductModel.created_by == created_by)
    return query


def apply_sort(
    query: Query, field: Optional[str], direction: Optional[str], field_map: dict
) -> Query:
    if field and direction and field in field_map:
        col = field_map[field]
        if direction.lower() == "asc":
            return query.order_by(col.asc())
        elif direction.lower() == "desc":
            return query.order_by(col.desc())
    return query


@router.get("/{product_sku}")
async def get_product_detail(product_sku: str, db: Session = Depends(get_db)):
    product = (
        db.query(ProductModel)
        .options(
            joinedload(ProductModel.creator),
            joinedload(ProductModel.category),
        )
        .filter(ProductModel.sku == product_sku)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "message": "Product retrieve successful",
        "data": ProductSchema.model_validate(product, from_attributes=True),
    }


@router.get("/")
async def get_product_lists(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    created_by: Optional[str] = None,
    sort_price: Optional[str] = None,
    sort_cost_price: Optional[str] = None,
    sort_name: Optional[str] = None,
    sort_created_at: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
):
    query = db.query(ProductModel)

    pipeline: List[Callable[[Query], Query]] = [
        lambda q: apply_search(q, search),
        lambda q: apply_filter_category(q, category_id),
        lambda q: apply_filter_created_by(q, created_by),
        lambda q: apply_sort(q, "price", sort_price, {"price": ProductModel.price}),
        lambda q: apply_sort(
            q, "cost_price", sort_cost_price, {"cost_price": ProductModel.cost_price}
        ),
        lambda q: apply_sort(q, "name", sort_name, {"name": ProductModel.name}),
        lambda q: apply_sort(
            q, "created_at", sort_created_at, {"created_at": ProductModel.created_at}
        ),
    ]

    for step in pipeline:
        query = step(query)

    total = query.count()
    products = query.offset(skip).limit(limit).all()
    product_list = [
        ProductSecondarySchema.model_validate(product, from_attributes=True)
        for product in products
    ]
    return {
        "message": "Retrieved product list",
        "data": product_list,
        "total": total,
        "limit": limit,
        "skip": skip,
    }


@router.post("/")
async def create_product(
    req: ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    if req.category_identifier:
        cat = (
            db.query(CategoryModel)
            .filter(CategoryModel.identifier == req.category_identifier)
            .first()
        )

    product = ProductModel(
        name=req.name,
        description=req.description,
        sku=req.sku,
        price=req.price,
        cost_price=req.cost_price,
        avatar=req.avatar,
        status=req.status,
        created_by=user["sub"],
        category_id=cat.id,
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)
    except IntegrityError as e:
        db.rollback()
        if 'unique constraint "product_sku_key"' in str(e.orig):
            raise HTTPException(status_code=400, detail="Sku already exists")
        raise HTTPException(status_code=400, detail="Database integerity error")

    return {"message": "product added succesfully"}


@router.patch("/{product_id}")
async def update(
    req: ProductUpdateSchema,
    product_id: uuid.UUID = Path(..., description="The UUID of the product"),
    db: Session = Depends(get_db),
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Unable to find the product")

    updated_data = req.model_dump(exclude_unset=True)

    if "category_identifier" in updated_data:
        category_identifier = updated_data.pop("category_identifier")
        if category_identifier:
            category = (
                db.query(CategoryModel)
                .filter(CategoryModel.identifier == category_identifier)
                .first()
            )
            if not category:
                raise HTTPException(
                    status_code=404,
                    detail="Unable to find category with the provided identifier",
                )
            product.category_id = category.id

    for field, value in updated_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to update the product")

    return {
        "message": "product updated successfully",
        "data": ProductSchema.model_validate(product, from_attributes=True),
    }
