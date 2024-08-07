import re
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output/automation_log.log"),
        logging.StreamHandler()
    ]
)

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Edge(chrome_options)
    driver.get('https://www.latimes.com/')
    driver.maximize_window()

    # First Page, open the Search bar and send the text
    xpath_pesquisa = '/html/body/ps-header/header/div[2]/button'
    xpath_search = '/html/body/ps-header/header/div[2]/div[2]/form/label/input'

    search_phrase = 'Olympics'

    # Everything that I will use
    class_title = 'promo-title'
    class_date = 'promo-timestamp'
    class_description = 'promo-description'
    class_image = 'image'

    try:
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath_pesquisa))
        ).click()
    finally:
        logging.info("Clicked on the search button")

    try:
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath_search))
        )
    finally:
        element.send_keys(search_phrase)
        element.send_keys(Keys.RETURN)
        logging.info("Search phrase entered and search initiated")

    # Starts the news reading
    articles = driver.find_elements(By.XPATH, '//ul[@class="search-results-module-results-menu"]/li')
    logging.info(f"Found {len(articles)} articles")

    first_article_date = None
    if articles:
        first_article_date = articles[0].find_element(By.CLASS_NAME, class_date).text
        logging.info(f"First article date: {first_article_date}")

    # Prepare data storage
    data = []

    for article in articles:
        try:
            title = article.find_element(By.CLASS_NAME, class_title).text
            description = article.find_element(By.CLASS_NAME, class_description).text
            date = article.find_element(By.CLASS_NAME, class_date).text

            # Only process articles that have the same date as the first article
            if date != first_article_date:
                continue

            # Get image link and image name
            img = article.find_element(By.CLASS_NAME, class_image)
            image_alt = img.get_attribute('alt')

            count_phrases = title.lower().count(search_phrase.lower()) + description.lower().count(search_phrase.lower())

            # Check if the title or description contains any amount of money
            money_pattern = r'(\$\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:,\d{3})*\s*(?:dollars|USD))'
            contains_money = bool(re.search(money_pattern, title + description))

            logging.info(f"Processed article: {title}")

        except Exception as e:
            logging.warning(f"Failed to process article: {e}")
            continue

        img.screenshot(f"output/{title}.png")
        logging.info(f"Saved screenshot for: {title}")

        # Store the data
        data.append({
            'title': title,
            'date': date,
            'description': description,
            'image': f"{title}.png",
            'image_alt': image_alt,
            'count_phrases': count_phrases,
            'contains_money': contains_money
        })

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save to Excel
    df.to_excel('output/latimes_olympics_news.xlsx', index=False)
    logging.info("Data saved to Excel")

    # Close the WebDriver
    driver.quit()

if __name__ == "__main__":
    main()