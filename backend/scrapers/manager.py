import logging
from database import SessionLocal
from scrapers.gkzx_scraper import GKZXScraper

logger = logging.getLogger(__name__)


class ScraperManager:
    def __init__(self):
        self.scrapers = [GKZXScraper()]

    def scrape_universities(self):
        db = SessionLocal()
        try:
            for scraper in self.scrapers:
                universities = scraper.scrape_universities()
                for u in universities:
                    db.merge(u)
                db.commit()
                logger.info(f"Scraped {len(universities)} universities from {scraper.__class__.__name__}")
        finally:
            db.close()

    def scrape_scores(self, province_name: str, year: int):
        db = SessionLocal()
        try:
            for scraper in self.scrapers:
                scores = scraper.scrape_scores(province_name, year)
                for s in scores:
                    db.merge(s)
                db.commit()
                logger.info(f"Scraped {len(scores)} scores for {province_name} {year}")
        finally:
            db.close()
