from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import University, Province

router = APIRouter()


@router.get("/universities")
def list_universities(
    province_id: int | None = Query(None, description="省份ID"),
    level: str | None = Query(None, description="院校层级: 985/211/双一流/普通"),
    utype: str | None = Query(None, description="院校类型"),
    keyword: str | None = Query(None, description="名称搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(University)
    if province_id:
        q = q.filter(University.province_id == province_id)
    if level:
        q = q.filter(University.level == level)
    if utype:
        q = q.filter(University.utype == utype)
    if keyword:
        q = q.filter(University.name.contains(keyword))

    total = q.count()
    items = q.order_by(
        University.level.desc(),
        University.name
    ).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "province_id": u.province_id,
                "province_name": u.province.name if u.province else "",
                "level": u.level,
                "type": u.utype,
                "website": u.website,
                "logo_url": u.logo_url,
            }
            for u in items
        ],
    }


@router.get("/universities/{university_id}")
def get_university(university_id: int, db: Session = Depends(get_db)):
    u = db.query(University).filter(University.id == university_id).first()
    if not u:
        return {"error": "Not found"}, 404
    return {
        "id": u.id,
        "name": u.name,
        "province_id": u.province_id,
        "province_name": u.province.name if u.province else "",
        "level": u.level,
        "type": u.utype,
        "website": u.website,
        "logo_url": u.logo_url,
    }


@router.get("/provinces")
def list_provinces(db: Session = Depends(get_db)):
    return [
        {"id": p.id, "name": p.name, "gaokao_mode": p.gaokao_mode}
        for p in db.query(Province).all()
    ]
