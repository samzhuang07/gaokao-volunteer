from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Major

router = APIRouter()


@router.get("/majors")
def list_majors(
    category: str | None = Query(None, description="学科门类"),
    keyword: str | None = Query(None, description="名称搜索"),
    db: Session = Depends(get_db),
):
    q = db.query(Major)
    if category:
        q = q.filter(Major.category == category)
    if keyword:
        q = q.filter(Major.name.contains(keyword))

    items = q.order_by(Major.category, Major.name).all()
    return {
        "total": len(items),
        "items": [
            {"id": m.id, "name": m.name, "category": m.category, "code": m.code}
            for m in items
        ],
    }


@router.get("/majors/categories")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Major.category).distinct().order_by(Major.category).all()
    return [c[0] for c in cats]
