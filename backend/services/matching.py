from sqlalchemy.orm import Session
from models import AdmissionScore, University, Major
from sqlalchemy import func, distinct


class MatchEngine:
    def __init__(self, db: Session):
        self.db = db

    def match(self, province_id: int, score: float, rank: int, subject_group: str) -> list:
        """Find all university-major combinations for a given province and score profile."""

        # Get all distinct university-major pairs that have scores in this province
        # and match the subject group (or are "不限")
        latest_year = (
            self.db.query(func.max(AdmissionScore.year))
            .filter(AdmissionScore.province_id == province_id)
            .scalar()
        ) or 2025

        scores = (
            self.db.query(AdmissionScore)
            .filter(
                AdmissionScore.province_id == province_id,
                AdmissionScore.year == latest_year,
                AdmissionScore.subject_group.in_([subject_group, "不限"]),
            )
            .all()
        )

        results = []
        seen = set()
        for s in scores:
            key = (s.university_id, s.major_id)
            if key in seen:
                continue
            seen.add(key)

            results.append({
                "university_id": s.university_id,
                "university_name": s.university.name,
                "university_level": s.university.level,
                "university_type": s.university.utype,
                "major_id": s.major_id,
                "major_name": s.major.name,
                "major_category": s.major.category,
                "avg_score": s.avg_score,
                "avg_rank": s.avg_rank,
                "min_score": s.min_score,
                "min_rank": s.min_rank,
                "max_score": s.max_score,
                "year": s.year,
                "batch": s.batch,
                "subject_group": s.subject_group,
                "enrollment_count": s.enrollment_count,
            })

        return results
