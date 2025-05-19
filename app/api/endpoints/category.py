from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import get_db
from app.schema.category import (
    CategoryCreate,
    Category as CategorySchema,
)
from app.models.category import Category as CategoryModel


router = APIRouter(
    prefix="/category",
    tags=["category"],
    responses={404: {"detail": "Not found"}},
)


@router.post("/")
async def create_category(req: CategoryCreate, db: Session = Depends(get_db)):
    category = CategoryModel(
        name=req.name,
        description=req.description,
        status=req.status,
        identifier=req.identifier,
        parent_id=req.parent_id,
    )

    try:
        db.add(category)
        db.commit()
        db.refresh(category)
    except IntegrityError as e:
        db.rollback()
        if 'unique constraint "category_identifier_key"' in str(e.orig):
            raise HTTPException(
                status_code=400, detail="category identifier already exists"
            )

    return {
        "message": "category added successfully",
        "data": CategorySchema.model_validate(category, from_attributes=True),
    }


@router.get("/{identifier}")
async def category_details(
    identifier: str,
    db: Session = Depends(get_db),
):
    def build_category_detail(category):
        if not category:
            return None
        parent = build_category_detail(category.parent) if category.parent else None
        cat_data = CategorySchema.model_validate(
            category, from_attributes=True
        ).model_dump()
        cat_data["parent"] = parent
        return cat_data

    category = (
        db.query(CategoryModel).filter(CategoryModel.identifier == identifier).first()
    )

    if not category:
        raise HTTPException(
            status_code=404, detail="unable to find category, invalid identifier"
        )

    return {
        "message": "retrieved category details",
        "data": build_category_detail(category),
    }


@router.get("/")
async def categories(db: Session = Depends(get_db)):
    categories = db.query(CategoryModel).all()

    data = [
        CategorySchema.model_validate(category, from_attributes=True)
        for category in categories
    ]

    return {"message": "successfully fetched the categories list", "data": data}
