from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.schema.sales_channel import (
    SalesChannelCreate,
    SalesChannel as SalesChannelSchema,
)
from app.api.dependencies import get_db
from app.models.sales_channel import SalesChannel as SalesChannelModel

router = APIRouter(
    prefix="/sales-channels",
    tags=["sales-channels"],
    responses={404: {"detail": "Not Found"}},
)


@router.get("/")
async def get_sales_channel(db: Session = Depends(get_db)):
    channels = db.query(SalesChannelModel).all()

    data = [
        SalesChannelSchema.model_validate(channel, from_attributes=True)
        for channel in channels
    ]

    return {"message": "retrive sales channel list", "data": data}


@router.post("/")
async def add_sales_channel(req: SalesChannelCreate, db: Session = Depends(get_db)):
    channel = SalesChannelModel(
        name=req.name,
        status=req.status,
    )

    try:
        db.add(channel)
        db.commit()
        db.refresh(channel)
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
            status_code=500, detail="unable to add sales channel at the moment"
        )

    return {
        "message": "added sales channel",
        "data": SalesChannelSchema.model_validate(channel, from_attributes=True),
    }
