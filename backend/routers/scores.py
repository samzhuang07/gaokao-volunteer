from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import AdmissionScore, University, Major, Province

router = APIRouter()


@router.get("/scores")
def list_scores(
    university_id: int | None = Query(None),
    major_id: int | None = Query(None),
    province_id: int | None = Query(None),
    year: int | None = Query(None),
    batch: str | None = Query(None),
    subject_group: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(AdmissionScore).options(
        joinedload(AdmissionScore.university),
        joinedload(AdmissionScore.major),
        joinedload(AdmissionScore.province),
    )
    if university_id:
        q = q.filter(AdmissionScore.university_id == university_id)
    if major_id:
        q = q.filter(AdmissionScore.major_id == major_id)
    if province_id:
        q = q.filter(AdmissionScore.province_id == province_id)
    if year:
        q = q.filter(AdmissionScore.year == year)
    if batch:
        q = q.filter(AdmissionScore.batch == batch)
    if subject_group:
        q = q.filter(AdmissionScore.subject_group == subject_group)

    total = q.count()
    items = q.order_by(AdmissionScore.avg_score.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": s.id,
                "university_id": s.university_id,
                "university_name": s.university.name,
                "university_level": s.university.level,
                "major_id": s.major_id,
                "major_name": s.major.name,
                "major_category": s.major.category,
                "province_id": s.province_id,
                "province_name": s.province.name,
                "year": s.year,
                "batch": s.batch,
                "subject_group": s.subject_group,
                "min_score": s.min_score,
                "min_rank": s.min_rank,
                "avg_score": s.avg_score,
                "avg_rank": s.avg_rank,
                "max_score": s.max_score,
                "enrollment_count": s.enrollment_count,
            }
            for s in items
        ],
    }


@router.get("/scores/history")
def score_history(
    university_id: int = Query(...),
    major_id: int = Query(...),
    province_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Get 3-year score history for a specific university-major-province combination."""
    scores = (
        db.query(AdmissionScore)
        .filter(
            AdmissionScore.university_id == university_id,
            AdmissionScore.major_id == major_id,
            AdmissionScore.province_id == province_id,
        )
        .order_by(AdmissionScore.year.desc())
        .all()
    )
    return [
        {
            "year": s.year,
            "min_score": s.min_score,
            "min_rank": s.min_rank,
            "avg_score": s.avg_score,
            "avg_rank": s.avg_rank,
            "batch": s.batch,
            "subject_group": s.subject_group,
        }
        for s in scores
    ]
