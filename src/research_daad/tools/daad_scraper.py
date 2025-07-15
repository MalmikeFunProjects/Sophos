import json
import time
import logging
from urllib.parse import urljoin
from typing import List, Dict, Optional

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class DAADScholarshipScraper:
    """Web scraper for DAAD scholarship database"""

    def __init__(self, headless: bool = True):
        """Initialize the scraper with Chrome driver"""
        self.base_url = "https://www2.daad.de"
        self.search_url = "https://www2.daad.de/deutschland/stipendium/datenbank/en/21148-scholarship-database/"
        self.scholarships = []
        self.driver = None
        self.logger = self._setup_logging()
        self.setup_driver(headless)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def setup_driver(self, headless: bool = True) -> None:
        """Setup Chrome driver with optimized options"""
        chrome_options = Options()

        # Performance and stability options
        options_list = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images"  # Faster loading
        ]

        if headless:
            options_list.append("--headless")

        for option in options_list:
            chrome_options.add_argument(option)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def _handle_cookie_popup(self) -> None:
        """Handle cookie consent popup if present"""
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Accept')]")
                )
            )
            accept_button.click()
            self.logger.info("Cookie consent accepted")
            time.sleep(2)
        except TimeoutException:
            self.logger.info("No cookie popup found")

    def get_page_source(self, url: str) -> Optional[str]:
        """Get page source using Selenium with error handling"""
        try:
            self.driver.get(url)
            self._handle_cookie_popup()

            # Wait for search results to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ul.resultlist > li.entry")
                )
            )
            time.sleep(2)  # Allow dynamic content to load
            return self.driver.page_source

        except TimeoutException:
            self.logger.error(f"Timeout loading page: {url}")
            return None

    def extract_scholarship_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        The function `extract_scholarship_links` parses a BeautifulSoup object to
        extract scholarship links from a search results page and returns them in a
        list of dictionaries containing the URL and title of each scholarship.

        :param soup: The `soup` parameter in the `extract_scholarship_links` method
        is expected to be an instance of the BeautifulSoup class. BeautifulSoup is a
        Python library for pulling data out of HTML and XML files. In this context,
        the `soup` parameter is used to represent the parsed HTML content of
        :type soup: BeautifulSoup
        :return: A list of dictionaries containing the extracted scholarship links,
        where each dictionary has keys 'url' and 'title' corresponding to the URL
        and title of the scholarship respectively.
        """
        """Extract scholarship links from search results page"""
        scholarship_links = []
        results = soup.select('ul.resultlist > li.entry')

        for result in results:
            try:
                link_tag = result.find('h2').find('a')
                if link_tag and link_tag.get('href'):
                    full_url = urljoin(self.base_url, link_tag['href'])
                    title = link_tag.get_text(strip=True).replace('\xa0• DAAD', '')
                    scholarship_links.append({
                        'url': full_url,
                        'title': title
                    })
            except Exception as e:
                self.logger.warning(f"Error extracting link: {e}")
                continue

        return scholarship_links

    def _click_application_requirements_tab(self) -> None:
        """Click on application requirements tab and handle form if present"""
        try:
            tab_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "li#bewerbungsvoraussetzungen > a")
                )
            )
            self.driver.execute_script("arguments[0].click();", tab_link)
            self.logger.info("Clicked on 'Application requirements' tab")

            # Handle eligibility form if present
            self._handle_eligibility_form()

        except TimeoutException:
            self.logger.warning("Could not find application requirements tab")

    def _handle_eligibility_form(self) -> None:
        """Handle eligibility form by selecting first valid option in each dropdown"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "select-application-info-form"))
            )
            self.logger.info("Eligibility form detected. Submitting form...")

            # Select first non-empty option from each dropdown
            selects = self.driver.find_elements(
                By.CSS_SELECTOR, "#select-application-info-form select"
            )

            for select_elem in selects:
                options = select_elem.find_elements(By.TAG_NAME, "option")
                for option in options:
                    if option.get_attribute("value").strip():
                        self.driver.execute_script("arguments[0].selected = true;", option)
                        self.driver.execute_script(
                            "arguments[0].dispatchEvent(new Event('change'))",
                            select_elem
                        )
                        self.logger.info(f"Selected option: {option.text}")
                        break

            time.sleep(1)

            # Submit form
            submit_button = self.driver.find_element(By.ID, "stipdb-submit-detail")
            self.driver.execute_script("arguments[0].click();", submit_button)
            self.logger.info("Form submitted successfully")
            time.sleep(2)

        except TimeoutException:
            self.logger.info("No eligibility form detected")

    def get_scholarship_details_page(self, url: str) -> Optional[str]:
        """Load scholarship details page and handle interactive elements"""
        try:
            self.driver.get(url)

            # Wait for main content to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "ifa-stipendien-detail"))
            )

            # Click application requirements tab
            self._click_application_requirements_tab()

            return self.driver.page_source

        except TimeoutException:
            self.logger.error(f"Timeout loading scholarship page: {url}")
            return None

    def extract_scholarship_details(self, url: str, title: str) -> Optional[Dict]:
        """Extract detailed scholarship information from individual page"""
        try:
            self.logger.info(f"Extracting details for: {title}")
            page_source = self.get_scholarship_details_page(url)

            if not page_source:
                return None

            soup = BeautifulSoup(page_source, 'html.parser')

            scholarship_data = {
                'title': title,
                'url': url,
                'status': 'active',
                'summary': None,
                'h3_details': {}
            }

            # Extract content from different sections
            section_ids = [
                'ueberblick', 'voraussetzungen', 'prozess',
                'kontaktberatung', 'bewerbung'
            ]

            for section_id in section_ids:
                section = soup.find('div', id=section_id)
                if section:
                    self._extract_section_content(section, scholarship_data)

            return scholarship_data

        except Exception as e:
            self.logger.error(f"Error extracting details from {url}: {e}")
            return None

    def _extract_section_content(self, section: Tag, scholarship_data: Dict) -> None:
        """Extract content from a specific section"""
        current_key = None
        buffer = []

        for elem in section.children:
            if isinstance(elem, Tag):
                if elem.name == 'h3':
                    # Save previous content block
                    if current_key and buffer:
                        scholarship_data['h3_details'][current_key] = '\n'.join(buffer).strip()

                    current_key = elem.get_text(strip=True)
                    buffer = []

                elif current_key and elem.name in ['p', 'ul', 'ol']:
                    buffer.append(elem.get_text(separator='\n', strip=True))

        # Save last content block
        if current_key and buffer:
            scholarship_data['h3_details'][current_key] = '\n'.join(buffer).strip()

    def scrape_scholarships(self) -> List[Dict]:
        """Main method to scrape all scholarships"""
        self.logger.info("Starting DAAD scholarship scraping...")

        try:
            # Get first page to determine total pages
            page_url = f"{self.search_url}?status=&origin=&subjectGrps=&daad=&intention=&q=&page=1&back=1"
            page_source = self.get_page_source(page_url)

            if not page_source:
                self.logger.error("Failed to load first page")
                return []

            soup = BeautifulSoup(page_source, 'html.parser')
            self._process_page_scholarships(soup)
            time.sleep(2)  # Respectful delay between pages

            return self.scholarships

        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return self.scholarships

    def _process_page_scholarships(self, soup: BeautifulSoup) -> None:
        """Process scholarships from a single page"""
        scholarship_links = self.extract_scholarship_links(soup)
        self.logger.info(f"Found {len(scholarship_links)} scholarships on page")

        for i, link_data in enumerate(scholarship_links, 1):
            self.logger.info(f"Processing scholarship {i}/{len(scholarship_links)}: {link_data['title']}")

            scholarship_details = self.extract_scholarship_details(
                link_data['url'], link_data['title']
            )

            if scholarship_details:
                self.scholarships.append(scholarship_details)
                self.logger.info(f"Successfully extracted: {scholarship_details['title']}")
            else:
                self.logger.warning(f"Failed to extract: {link_data['title']}")

            time.sleep(1)  # Respectful delay

    def save_to_json(self, filename: str = 'daad_scholarships.json') -> None:
        """Save scholarships to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scholarships, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self.scholarships)} scholarships to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")

    def close(self) -> None:
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Main function to run the scraper"""
    with DAADScholarshipScraper(headless=False) as scraper:
        try:
            # Scrape scholarships (limit to first 3 pages for testing)
            scholarships = scraper.scrape_scholarships()

            # Save to JSON
            scraper.save_to_json('daad_scholarships.json')

            print("\nScraping completed!")
            print(f"Total scholarships found: {len(scholarships)}")

            # Display sample scholarship
            if scholarships:
                print("\nSample scholarship:")
                print(json.dumps(scholarships[0], indent=2))

        except KeyboardInterrupt:
            print("\nScraping interrupted by user")
        except Exception as e:
            print(f"Error during scraping: {e}")


if __name__ == "__main__":
    main()
