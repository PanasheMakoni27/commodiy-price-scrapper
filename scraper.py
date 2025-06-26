import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

#I simply used a data structure class to hold commodity price information, along with the timestamp and currency.
@dataclass
class CommodityPrice:
    name: str
    price: float
    timestamp: datetime
    currency: str = "USD"
    unit: str = "per tonne"


class CommodityScraper:
    def __init__(self, target_commodities: List[str] = None):
        self.target_commodities = target_commodities or ['Lithium', 'Lead', 'Cobalt']
        self.base_url = 'https://tradingeconomics.com/commodities'
        self.session = self._setup_session()
        self._setup_logging()
        
    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        return session
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('commodity_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_page(self) -> BeautifulSoup:
        #I fetched the commodities webpage and parsed it using BeautifulSoup. I used BeautifulSoup library because it simply passes HTML and XML documents easily. 
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch page: {e}")
            raise

        #In this instance, I was trying to extract the price from the price string from the HTML Cell
    def extract_price_from_cell(self, price_cell) -> Optional[str]:
        strategies = [
            lambda c: c.find(id='p'),
            lambda c: c.find(class_=re.compile('price', re.I)),
            lambda c: next((e.get_text(strip=True) for tag in ['span', 'div', 'strong'] for e in c.find_all(tag) if re.search(r'\d+', e.get_text(strip=True))), None),
            lambda c: c.get_text(strip=True)
        ]
        for strategy in strategies:
            result = strategy(price_cell)
            if result:
                return result
        return None
    
    def clean_commodity_name(self, raw_name: str) -> str:
        #This was an important step in the process, because I had to clean the line breaks and unwanted characters from the commidities which I want to extract which were lead, lithium and cobalt.
        name = re.split(r'\n|\r', raw_name)[0].strip()
        return re.sub(r'[^\w\s-]', '', name).strip()
    
    def parse_price(self, price_text: str) -> Optional[float]:
        #I had to convert the string extracted in the earlier steps into a float value so that I could use the float value in my plotting process. 
        try:
            clean = re.sub(r'[^\d.,]', '', price_text).replace(',', '')
            return float(clean) if clean else None
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse price: {price_text}")
            return None
    
    def is_target_commodity(self, name: str) -> Optional[str]:
        #I had to find the extract commodities that I needed. So this function basically goes through the tables on the page to find the commodities that I needed and their extract prices. 
        for target in self.target_commodities:
            if target.lower() in name.lower():
                return target
        return None
    
    def scrape_all_tables(self, soup: BeautifulSoup) -> Dict[str, CommodityPrice]:
        tables = soup.find_all('table')
        results = {}
        timestamp = datetime.now()
        
        for table in tables:
            rows = table.find_all('tr')
            # I want to skip tables that had insufficient rows as this would corrupt my data. 
            if len(rows) < 2:
                continue
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    raw_name = cols[0].get_text(strip=True)
                    name = self.clean_commodity_name(raw_name)
                    target = self.is_target_commodity(name)
                    if not target:
                        continue #this step is to keep it moving if its not one of the three commodities that I was tasked to extract. 
                    price_text = self.extract_price_from_cell(cols[1])
                    price_value = self.parse_price(price_text)
                    if price_value is not None:
                        #This step is for the storage of price data with timestamps for later use, if needed or if project is expended to other commodities. 
                        results[target] = CommodityPrice(
                            name=target,
                            price=price_value,
                            timestamp=timestamp
                        )
        return results
    
    def scrape_commodities(self) -> Dict[str, CommodityPrice]:
        #This is where the task, actually started and the fun begin. This is my main method to conduct scrapting and to handle an errors that may cause the program to crash. 
        try:
            soup = self.fetch_page()
            prices = self.scrape_all_tables(soup)
            found = set(prices.keys())
            missing = set(self.target_commodities) - found
            if missing:
                self.logger.warning(f"Missing commodities: {missing}")
            return prices
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            return {}


class CommodityVisualizer:
    def __init__(self):
        #I set the plot style and color palette for my visualization.
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def create_price_chart(self, prices: Dict[str, CommodityPrice], save_path: str = None) -> None:
        #I want to show these commodities in the form of a Bar graph due to the simplicity of the visual. Very easy to understand. 
        if not prices:
            print("No price data available for visualization")
            return
        
        commodities = list(prices.keys())
        values = [prices[c].price for c in commodities]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.bar(commodities, values, color=['#2E8B57', '#4169E1', '#DC143C'][:len(commodities)],
                      alpha=0.8, edgecolor='black', linewidth=1.2)
        
        # In this step, I was basically setting up clear and proffesional labels for my visual. 
        ax.set_title('Commodity Prices', fontsize=16, fontweight='bold')
        ax.set_xlabel('Commodity', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price (USD per tonne)', fontsize=12, fontweight='bold')

        # I was adding bars with the exact prices so that the read can easily interpret the information presented to them. 
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 5,
                    f'{value:,.0f}', ha='center', va='bottom', fontsize=11)
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        
        timestamp = list(prices.values())[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')
        plt.figtext(0.02, 0.02, f'Data collected: {timestamp}', fontsize=8, style='italic')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_summary_table(self, prices: Dict[str, CommodityPrice]) -> pd.DataFrame:
        if not prices:
            return pd.DataFrame()
        return pd.DataFrame([{
            'Commodity': p.name,
            'Price (USD/tonne)': f"{p.price:,.2f}",
            'Timestamp': p.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for p in prices.values()])


def main():
    #I was telling the program that I only want 3 commodities to be visualised which were lithium, Lead and Cobalt
    target_commodities = ['Lithium', 'Lead', 'Cobalt']
    scraper = CommodityScraper(target_commodities)
    prices = scraper.scrape_commodities()
    
    if not prices:
        print("No prices were scraped.")
        return
    
    for name, p in prices.items():
        print(f"{name}: ${p.price:,.2f} per tonne")

    #I was telling this program to show the results in a bar chart
    visualizer = CommodityVisualizer()
    visualizer.create_price_chart(prices, save_path='commodity_prices_chart.png')

    #
    summary = visualizer.create_summary_table(prices)
    print("\nCommodity Price Summary:")
    print(summary.to_string(index=False))
    summary.to_csv('commodity_prices_summary.csv', index=False)
    print("\nSummary saved to: commodity_prices_summary.csv")


if __name__ == "__main__":
    main()