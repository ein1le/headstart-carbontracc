from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import time
from selenium.webdriver.common.by import By
import pandas as pd


class Scraper:
    def __init__(self):
        self.products = []
        self.setup_driver()
        self.main_cat = ''
        self.sub_cat = ''
        
        
    def setup_driver(self):
        print("setting up driver")
        options = uc.ChromeOptions() 
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')
        options.add_argument('--start-maximized')

        
        UA = UserAgent() 
        user_agent = UA.random
        options.add_argument(f'user-agent={user_agent}') 
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)
        
        
    
    def accept_cookies(self):
        print("cookies accepting")
        try:
            time.sleep(random.uniform(4, 6))  
            cookie_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            time.sleep(random.uniform(1, 2))
            cookie_btn.click()
            time.sleep(random.uniform(3, 5))
        except TimeoutException:
            pass  
        
    def scroll_page(self):
        print("scrolling")
        total = self.driver.execute_script("return document.body.scrollHeight")
        current = 0
        step = random.randint(200, 400) 
        
        while current < total:
            current += step
            self.driver.execute_script(f"window.scrollTo(0, {current});")
            time.sleep(random.uniform(0.5, 1))
    def scrape_product(self, product):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", product)
            time.sleep(random.uniform(0.3, 0.7))
            
            name = product.find_element(By.CSS_SELECTOR, "[data-testid='product-tile-description']").text.strip()
            
            try:
                img = product.find_element(By.CSS_SELECTOR, "img[data-testid='pt-image']").get_attribute("src")
            except NoSuchElementException:
                img = "No Image "
            
            return {
                "Product name": name,
                "Main Category": self.main_cat,
                "Subcategory": self.sub_cat,
                "Image": img
            }
        except Exception:
            return None  

    def scrape_category(self, url, main_cat, sub_cat):
        print("scraping by cat")
        self.main_cat = main_cat
        self.sub_cat = sub_cat
        
        self.driver.get(url)
        time.sleep(random.uniform(5, 7))  
        self.accept_cookies()
        
        page = 1
        while True:
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid^='product-tile']")))
                self.scroll_page()
                time.sleep(random.uniform(2, 3))
                
                products = self.driver.find_elements(By.CSS_SELECTOR, "article[data-testid^='product-tile']")
                
                for product in products:
                    product_data = self.scrape_product(product)
                    if product_data:
                        self.products.append(product_data)
                        time.sleep(random.uniform(0.5, 1))
                
                self.save_progress()
                
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='pagination-next-btn']")
                    if "disabled" in next_btn.get_attribute("class"):
                        break
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                    time.sleep(random.uniform(2, 3))
                    next_btn.click()
                    time.sleep(random.uniform(4, 6))
                    page += 1
                except NoSuchElementException:
                    break
                
            except Exception:
                break  

    def save_progress(self):
        print("saving progress")
        print('saving for:', self.products)
        if self.products:
            df = pd.DataFrame(self.products)
            df.to_csv("sainsburys_products.csv", index=False)

    def run(self):
        print("running")
        try:
            print('in try')
            for cat in categories:
                print(' in cat 1: ', cat)
                main_cat = cat["main_category"]
                print('using: ', main_cat, 'as main')
                for sub_cat in cat["subcategories"]:
                    print('using: ', sub_cat, 'as sub')
                    try:
                        self.scrape_category(
                            sub_cat["url"],
                            main_cat,
                            sub_cat["name"]
                        )
                        time.sleep(random.uniform(5, 7))
                    except Exception:
                        continue  
            
            self.save_progress()
            
        except Exception:
            pass  
        finally:
            self.driver.quit() 




categories = [
    # Meat and Fish
    {
        "main_category": "meat-and-fish",
        "subcategories": [
            {"name": "beef", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/beef/c:1020335"},
            {"name": "chicken", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/chicken/c:1020336"},
            {"name": "lamb", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/lamb/c:1020337"},
            {"name": "pork", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/pork/c:1020338"},
            {"name": "fish", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/meat-and-fish/fish/c:1020339"}
        ]
    },
    
    # Fruit and Vegetables
    {
        "main_category": "fruit-and-vegetables",
        "subcategories": [
            {"name": "fresh-fruit", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/fruit-and-vegetables/fresh-fruit/c:1020020"},
            {"name": "fresh-vegetables", "url": "https://www.sainsburys.co.uk/gol-ui/groceries/fruit-and-vegetables/fresh-vegetables/c:1020021"}
        ]
    },
]
if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()