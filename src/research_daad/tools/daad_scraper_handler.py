from src.research_daad.tools.daad_scraper import DAADScholarshipScraper
from crewai.tools import tool


@tool("scrape_daad_scholarships")
def scrape_daad_scholarships() -> str:
    """Scrapes all active scholarships from the DAAD database"""

    scraper = DAADScholarshipScraper(headless=True)
    all_scholarships = scraper.scrape_scholarships()
    if not all_scholarships:
        return "No scholarships found."
    return str(all_scholarships)
