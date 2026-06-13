"""Real score-rank lookup table built from official Gaokao score distribution data.

Data source: sdgedfegw/Gaokao-score-distribution (GitHub)
Covers all 31 mainland provinces, 1996-2024, all subject groups.
"""

import csv
import os
from typing import Optional

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "score_distribution.csv")

# Subject group name normalization
SUBJECT_NORMALIZE = {
    "物理类": "物理",
    "理科": "物理",
    "历史类": "历史",
    "文科": "历史",
    "3+3综合": "不限",
    "3+1+1综合": "不限",
    "综合": "不限",
}

# Province name normalization from GitHub data to our DB names
PROVINCE_NORMALIZE = {
    "北京": "北京", "天津": "天津", "上海": "上海", "重庆": "重庆",
    "河北": "河北", "山西": "山西", "辽宁": "辽宁", "吉林": "吉林",
    "黑龙江": "黑龙江", "江苏": "江苏", "浙江": "浙江", "安徽": "安徽",
    "福建": "福建", "江西": "江西", "山东": "山东", "河南": "河南",
    "湖北": "湖北", "湖南": "湖南", "广东": "广东", "广西": "广西",
    "海南": "海南", "四川": "四川", "贵州": "贵州", "云南": "云南",
    "西藏": "西藏", "陕西": "陕西", "甘肃": "甘肃", "青海": "青海",
    "宁夏": "宁夏", "新疆": "新疆", "内蒙古": "内蒙古",
}


class RankLookup:
    """Real score-to-rank lookup using official one-point-one-section tables."""

    def __init__(self):
        self._data: dict[tuple, dict[int, int]] = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        if not os.path.exists(CSV_PATH):
            return
        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prov_raw = row["省级行政区"]
                subj_raw = row.get("综合", "")
                year = row["年份"]
                try:
                    score = int(row["最高分"])
                    cum_rank = int(row["累计"])
                except (ValueError, KeyError):
                    continue

                prov = PROVINCE_NORMALIZE.get(prov_raw)
                subj = SUBJECT_NORMALIZE.get(subj_raw)
                if not prov or not subj:
                    continue

                key = (prov, year, subj)
                if key not in self._data:
                    self._data[key] = {}
                # Store score -> cumulative rank (lowest rank for this score)
                if score not in self._data[key] or cum_rank > self._data[key][score]:
                    self._data[key][score] = cum_rank
        self._loaded = True

    def score_to_rank(self, province: str, year: str | int, subject: str, score: float) -> int:
        """Convert a score to its approximate cumulative rank using real data."""
        self._load()
        year = str(year)
        subj = SUBJECT_NORMALIZE.get(subject, subject)

        key = (province, year, subj)
        if key not in self._data:
            # Fallback 1: try "不限" subject (for 3+3 provinces like Beijing, Shanghai)
            alt_key = (province, year, "不限")
            if alt_key in self._data:
                key = alt_key
        if key not in self._data:
            # Fallback 2: try nearby year
            for y_offset in range(-1, -4, -1):
                alt_key = (province, str(int(year) + y_offset), subj)
                if alt_key in self._data:
                    key = alt_key
                    break
            else:
                return 0

        table = self._data[key]
        score_int = int(round(score))

        # Exact match
        if score_int in table:
            return table[score_int]

        # Find nearest score
        scores = sorted(table.keys())
        for s in scores:
            if s <= score_int:
                return table[s]

        return table.get(scores[0], 0) if scores else 0

    def rank_to_score(self, province: str, year: str | int, subject: str, rank: int) -> Optional[float]:
        """Convert a rank to its approximate score using real data."""
        self._load()
        year = str(year)
        subj = SUBJECT_NORMALIZE.get(subject, subject)

        key = (province, year, subj)
        if key not in self._data:
            alt_key = (province, year, "不限")
            if alt_key in self._data:
                key = alt_key
        if key not in self._data:
            for y_offset in range(-1, -4, -1):
                alt_key = (province, str(int(year) + y_offset), subj)
                if alt_key in self._data:
                    key = alt_key
                    break
            else:
                return None

        table = self._data[key]
        # Iterate scores descending: find the highest score where
        # cumulative count is at least the target rank
        for score in sorted(table.keys(), reverse=True):
            if table[score] >= rank:
                return float(score)
        return None


# Singleton
lookup = RankLookup()
