import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class GKZXScraper(BaseScraper):
    """Scraper for gaokao.com (高考直通车) and similar public education sites."""

    BASE_URL = "https://www.gaokao.com"

    def scrape_universities(self) -> list:
        """Scrape university list. Returns list of dicts with university fields."""
        results = []
        html = self.fetch(f"{self.BASE_URL}/daxue/")
        if not html:
            logger.warning("Failed to fetch university list from gaokao.com")
            return results

        soup = BeautifulSoup(html, "lxml")
        # Site structure may vary; this is the expected structure
        for item in soup.select(".school-list .school-item")[:500]:
            try:
                name_el = item.select_one(".school-name a")
                if not name_el:
                    continue
                name = name_el.text.strip()
                level_text = item.select_one(".school-tags")
                level = "普通"
                if level_text:
                    tags = level_text.text.strip()
                    if "985" in tags:
                        level = "985"
                    elif "211" in tags:
                        level = "211"
                    elif "双一流" in tags:
                        level = "双一流"

                results.append({
                    "name": name,
                    "level": level,
                    "utype": "综合",
                    "province_id": 1,
                })
            except Exception as e:
                logger.debug(f"Parse error for university item: {e}")
        return results

    def scrape_scores(self, province_name: str, year: int) -> list:
        """Scrape admission scores for a province and year. Returns list of dicts."""
        results = []
        url = f"{self.BASE_URL}/fenshuxian/"
        html = self.fetch(url, params={"province": province_name, "year": str(year)})
        if not html:
            logger.warning(f"Failed to fetch scores for {province_name} {year}")
            return results

        soup = BeautifulSoup(html, "lxml")
        for row in soup.select(".score-table tr")[1:]:
            try:
                cols = row.select("td")
                if len(cols) < 5:
                    continue
                results.append({
                    "university_name": cols[0].text.strip(),
                    "major_name": cols[1].text.strip() if len(cols) > 1 else "不限",
                    "min_score": float(cols[2].text.strip()) if cols[2].text.strip() else 0,
                    "min_rank": int(cols[3].text.strip()) if len(cols) > 3 and cols[3].text.strip() else 0,
                    "batch": cols[4].text.strip() if len(cols) > 4 else "本科批",
                    "year": year,
                })
            except (ValueError, IndexError) as e:
                logger.debug(f"Parse error for score row: {e}")
        return results
