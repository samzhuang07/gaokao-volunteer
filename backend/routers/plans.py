from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from database import get_db
from models import VolunteerPlan, VolunteerItem, University, Major

router = APIRouter()


@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(VolunteerPlan).order_by(VolunteerPlan.updated_at.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "province_id": p.province_id,
            "score": p.score,
            "rank": p.rank,
            "subject_group": p.subject_group,
            "item_count": len(p.items),
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in plans
    ]


@router.post("/plans")
def create_plan(
    name: str = Query("我的志愿方案"),
    province_id: int = Query(...),
    score: float = Query(...),
    rank: int = Query(...),
    subject_group: str = Query("物理"),
    db: Session = Depends(get_db),
):
    plan = VolunteerPlan(
        name=name,
        province_id=province_id,
        score=score,
        rank=rank,
        subject_group=subject_group,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return {"id": plan.id, "name": plan.name}


@router.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = (
        db.query(VolunteerPlan)
        .options(joinedload(VolunteerPlan.items))
        .filter(VolunteerPlan.id == plan_id)
        .first()
    )
    if not plan:
        return {"error": "Not found"}, 404

    items = []
    for item in sorted(plan.items, key=lambda x: x.priority):
        univ = db.query(University).get(item.university_id)
        major = db.query(Major).get(item.major_id)
        items.append({
            "id": item.id,
            "university_id": item.university_id,
            "university_name": univ.name if univ else "",
            "university_level": univ.level if univ else "",
            "major_id": item.major_id,
            "major_name": major.name if major else "",
            "major_category": major.category if major else "",
            "priority": item.priority,
            "note": item.note,
        })

    return {
        "id": plan.id,
        "name": plan.name,
        "province_id": plan.province_id,
        "score": plan.score,
        "rank": plan.rank,
        "subject_group": plan.subject_group,
        "items": items,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
    }


@router.put("/plans/{plan_id}")
def update_plan(
    plan_id: int,
    name: str | None = Query(None),
    db: Session = Depends(get_db),
):
    plan = db.query(VolunteerPlan).filter(VolunteerPlan.id == plan_id).first()
    if not plan:
        return {"error": "Not found"}, 404
    if name:
        plan.name = name
    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok"}


@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(VolunteerPlan).filter(VolunteerPlan.id == plan_id).first()
    if not plan:
        return {"error": "Not found"}, 404
    db.delete(plan)
    db.commit()
    return {"status": "ok"}


@router.post("/plans/{plan_id}/items")
def add_item(
    plan_id: int,
    university_id: int = Query(...),
    major_id: int = Query(...),
    note: str = Query(""),
    db: Session = Depends(get_db),
):
    plan = db.query(VolunteerPlan).filter(VolunteerPlan.id == plan_id).first()
    if not plan:
        return {"error": "Plan not found"}, 404

    max_priority = 0
    if plan.items:
        max_priority = max(i.priority for i in plan.items)

    item = VolunteerItem(
        plan_id=plan_id,
        university_id=university_id,
        major_id=major_id,
        priority=max_priority + 1,
        note=note,
    )
    db.add(item)
    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "priority": item.priority}


@router.delete("/plans/{plan_id}/items/{item_id}")
def remove_item(plan_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(VolunteerItem).filter(
        VolunteerItem.id == item_id, VolunteerItem.plan_id == plan_id
    ).first()
    if not item:
        return {"error": "Not found"}, 404
    db.delete(item)
    # Re-order remaining items
    plan = db.query(VolunteerPlan).filter(VolunteerPlan.id == plan_id).first()
    for idx, i in enumerate(sorted(plan.items, key=lambda x: x.priority)):
        i.priority = idx + 1
    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok"}


@router.put("/plans/{plan_id}/items/reorder")
def reorder_items(
    plan_id: int,
    item_ids: str = Query(..., description="Comma-separated item IDs in new order"),
    db: Session = Depends(get_db),
):
    plan = db.query(VolunteerPlan).filter(VolunteerPlan.id == plan_id).first()
    if not plan:
        return {"error": "Plan not found"}, 404

    ids = [int(x) for x in item_ids.split(",")]
    for idx, item_id in enumerate(ids):
        item = db.query(VolunteerItem).filter(
            VolunteerItem.id == item_id, VolunteerItem.plan_id == plan_id
        ).first()
        if item:
            item.priority = idx + 1

    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok"}
