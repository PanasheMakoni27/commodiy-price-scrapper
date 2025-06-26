# Commodity Price Scraper

# Project Overview
I developed this project to efficiently scrape real-time prices for **Lithium**, **Lead**, and **Cobalt** from [TradingEconomics.com/commodities](https://tradingeconomics.com/commodities).
The solution uses Python with `requests` and `BeautifulSoup` for scraping, saves data to CSV, and visualizes prices using **Matplotlib** and **Seaborn**.

# Key Features
- **Reliable scraping** of Lithium, Lead, and Cobalt prices, resilient to minor webpage changes
- **Stores timestamped price data** in `data/commodity_prices.csv` for historical tracking
- **Produces a summary table and clean bar chart** for quick price insights
- **Implements logging** for transparency and debugging
- **Modular, well-documented code** using Python classes and dataclasses
- **Prepared for deployment** with essential files and minimal dependencies

# Project Structure
- `scraper.py` — Core scraping and visualization logic
- `requirements.txt` — Required Python libraries
- `README.md` — Documentation
- `data/commodity_prices.csv` — Auto-generated dataset
- `screenshots/commodity-price-scrapper.md` — Optional chart reference

# How to Run
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Execute the scraper:**
   ```bash
   python scraper.py
   ```
3. **Review the generated CSV and price chart.**