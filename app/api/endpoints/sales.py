from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import date
from typing import Optional

from app.api.dependencies import get_db
from app.models.sales import Sales as SalesModel

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    responses={404: {"detail": "Not Found"}},
)


@router.get("/revenue")
def get_revenue(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    product_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    channel_id: Optional[str] = Query(None),
    group_by: Optional[str] = Query("day", description="day|week|month|year"),
):
    query = db.query(
        func.sum(SalesModel.amount).label("total_revenue"),
        func.count(SalesModel.id).label("total_sales"),
    )

    if group_by == "day":
        query = query.add_columns(func.date(SalesModel.sale_date).label("period"))
        query = query.group_by(func.date(SalesModel.sale_date))
    elif group_by == "week":
        query = query.add_columns(
            extract("year", SalesModel.sale_date).label("year"),
            extract("week", SalesModel.sale_date).label("week"),
        )
        query = query.group_by(
            extract("year", SalesModel.sale_date), extract("week", SalesModel.sale_date)
        )
    elif group_by == "month":
        query = query.add_columns(
            extract("year", SalesModel.sale_date).label("year"),
            extract("month", SalesModel.sale_date).label("month"),
        )
        query = query.group_by(
            extract("year", SalesModel.sale_date),
            extract("month", SalesModel.sale_date),
        )
    elif group_by == "year":
        query = query.add_columns(extract("year", SalesModel.sale_date).label("year"))
        query = query.group_by(extract("year", SalesModel.sale_date))
    else:
        raise HTTPException(status_code=400, detail="Invalid group_by value")

    filters = []
    if start_date:
        filters.append(SalesModel.sale_date >= start_date)
    if end_date:
        filters.append(SalesModel.sale_date <= end_date)
    if product_id:
        filters.append(SalesModel.product_id == product_id)
    if category_id:
        filters.append(SalesModel.category_id == category_id)
    if channel_id:
        filters.append(SalesModel.channel_id == channel_id)

    if filters:
        query = query.filter(and_(*filters))

    results = query.all()
    data = []
    for row in results:
        if hasattr(row, "_asdict"):
            data.append(row._asdict())
        elif isinstance(row, tuple):
            keys = row.keys() if hasattr(row, "keys") else []
            if keys:
                data.append({k: v for k, v in zip(keys, row)})
            else:
                data.append({"value_" + str(i): v for i, v in enumerate(row)})
        else:
            data.append({"value": row})
    return {"message": "Revenue data", "data": data}


@router.get("/compare")
def compare_revenue(
    db: Session = Depends(get_db),
    period1_start: date = Query(...),
    period1_end: date = Query(...),
    period2_start: date = Query(...),
    period2_end: date = Query(...),
    category_id: Optional[str] = Query(None),
):
    def get_revenue_for_period(start, end):
        q = db.query(func.sum(SalesModel.amount).label("revenue"))
        q = q.filter(SalesModel.sale_date >= start, SalesModel.sale_date <= end)
        if category_id:
            q = q.filter(SalesModel.category_id == category_id)
        return q.scalar() or 0

    revenue1 = get_revenue_for_period(period1_start, period1_end)
    revenue2 = get_revenue_for_period(period2_start, period2_end)
    return {
        "message": "Revenue comparison",
        "period1": {"start": period1_start, "end": period1_end, "revenue": revenue1},
        "period2": {"start": period2_start, "end": period2_end, "revenue": revenue2},
        "difference": revenue2 - revenue1,
    }


@router.get("/by-product")
def sales_by_product(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[str] = Query(None),
):
    query = db.query(
        SalesModel.product_id,
        func.sum(SalesModel.amount).label("total_revenue"),
        func.count(SalesModel.id).label("total_sales"),
    )
    if start_date:
        query = query.filter(SalesModel.sale_date >= start_date)
    if end_date:
        query = query.filter(SalesModel.sale_date <= end_date)
    if category_id:
        query = query.filter(SalesModel.category_id == category_id)
    query = query.group_by(SalesModel.product_id)

    results = query.all()
    data = [
        {
            "product_id": row[0],
            "total_revenue": row[1],
            "total_sales": row[2],
        }
        for row in results
    ]
    return {"message": "Sales by product", "data": data}


@router.get("/by-category")
def sales_by_category(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    query = db.query(
        SalesModel.category_id,
        func.sum(SalesModel.amount).label("total_revenue"),
        func.count(SalesModel.id).label("total_sales"),
    )
    if start_date:
        query = query.filter(SalesModel.sale_date >= start_date)
    if end_date:
        query = query.filter(SalesModel.sale_date <= end_date)
    query = query.group_by(SalesModel.category_id)

    results = query.all()
    data = [
        {
            "category_id": row[0],
            "total_revenue": row[1],
            "total_sales": row[2],
        }
        for row in results
    ]
    return {"message": "Sales by category", "data": data}
