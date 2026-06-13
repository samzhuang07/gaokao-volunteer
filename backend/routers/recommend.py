from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.matching import MatchEngine
from services.probability import ProbabilityCalculator
from services.discipline_rating import rating_service

router = APIRouter()

RATING_COLORS: dict[str, str] = {
    "A+": "#c41d7f", "A": "#cf1322", "A-": "#d4380d",
    "B+": "#d46b08", "B": "#d48806", "B-": "#7cb305",
    "C+": "#08979c", "C": "#1677ff", "C-": "#597ef7",
}


@router.get("/recommend")
def recommend(
    province_id: int = Query(..., description="目标省份ID"),
    score: float = Query(..., description="高考分数"),
    rank: int = Query(..., description="位次"),
    subject_group: str = Query("物理", description="选科组: 物理/历史/不限"),
    db: Session = Depends(get_db),
):
    engine = MatchEngine(db)
    calc = ProbabilityCalculator()
    matches = engine.match(province_id, score, rank, subject_group)
    enriched = calc.calculate_all(matches, rank)

    # Add real discipline evaluation rating for each result
    for item in enriched:
        rating = rating_service.get_rating(
            item.get("university_name", ""),
            item.get("major_category", ""),
        )
        item["discipline_rating"] = rating

    # Sort: reach first (lowest chance to highest), then match, then safety
    # Within each category, ascending probability (hardest first)
    category_order = {"reach": 0, "match": 1, "safety": 2}
    enriched.sort(key=lambda x: (category_order.get(x["category"], 99), x["probability"]))

    return {
        "total": len(enriched),
        "user_score": score,
        "user_rank": rank,
        "items": enriched,
    }
