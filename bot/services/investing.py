import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from utils import load_from_cache, save_to_cache

class InvestingParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_economic_calendar(self) -> List[Dict]:
        """Получить важные экономические события на сегодня."""
        cache_key = 'economic_calendar'
        cached_data = load_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            url = 'https://ru.investing.com/economic-calendar/'
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            events = []
            for event in soup.select('.js-event-item'):
                try:
                    time = event.select_one('.time').text.strip()
                    country = event.select_one('.country').text.strip()
                    name = event.select_one('.event').text.strip()
                    impact = len(event.select('.bull-icon.important'))  # 1-3 звезды важности
                    
                    # Получаем фактическое и прогнозное значения
                    actual = event.select_one('.actual')
                    actual = actual.text.strip() if actual else None
                    
                    forecast = event.select_one('.forecast')
                    forecast = forecast.text.strip() if forecast else None
                    
                    events.append({
                        'time': time,
                        'country': country,
                        'name': name,
                        'impact': impact,
                        'actual': actual,
                        'forecast': forecast
                    })
                except Exception:
                    continue
            
            # Сохраняем в кэш на 1 час
            save_to_cache(cache_key, events, expire_minutes=60)
            return events
            
        except Exception as e:
            print(f"Ошибка получения экономического календаря: {e}")
            return []
    
    def get_crypto_news(self) -> List[Dict]:
        """Получить последние новости по криптовалютам."""
        cache_key = 'crypto_news'
        cached_data = load_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        try:
            url = 'https://ru.investing.com/crypto/news'
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news = []
            for article in soup.select('.articleItem'):
                try:
                    title = article.select_one('.title').text.strip()
                    time = article.select_one('.date').text.strip()
                    link = article.select_one('a')['href']
                    
                    news.append({
                        'title': title,
                        'time': time,
                        'link': f"https://ru.investing.com{link}"
                    })
                except Exception:
                    continue
                    
                if len(news) >= 10:  # Ограничиваем 10 новостями
                    break
            
            # Сохраняем в кэш на 15 минут
            save_to_cache(cache_key, news, expire_minutes=15)
            return news
            
        except Exception as e:
            print(f"Ошибка получения новостей: {e}")
            return []

# Создаем единственный экземпляр
investing_parser = InvestingParser() 