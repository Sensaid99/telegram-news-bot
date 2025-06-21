import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class NewsService:
    """Сервис для работы с новостями."""
    
    def __init__(self):
        self.base_url = "https://api.cryptopanic.com/v1"
        self.api_key = "YOUR_API_KEY"  # Замените на ваш API ключ
        
    async def get_market_news(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Получает новости рынка за указанный период."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "auth_token": self.api_key,
                    "kind": "news",
                    "filter": "important",
                    "public": "true",
                    "published_after": (datetime.now() - timedelta(hours=hours)).isoformat()
                }
                
                async with session.get(f"{self.base_url}/posts/", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_news(data["results"])
                    else:
                        logger.error(f"Error fetching news: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_market_news: {e}")
            return []
            
    def _process_news(self, news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обрабатывает полученные новости."""
        processed_news = []
        
        for news in news_data:
            # Определяем влияние новости на рынок
            impact = self._analyze_impact(news)
            
            processed_news.append({
                "title": news["title"],
                "summary": news.get("metadata", {}).get("summary", ""),
                "source": news["source"]["title"],
                "url": news["url"],
                "published_at": news["published_at"],
                "impact": impact,
                "currencies": news.get("currencies", []),
                "categories": news.get("categories", [])
            })
            
        return processed_news
        
    def _analyze_impact(self, news: Dict[str, Any]) -> str:
        """Анализирует влияние новости на рынок."""
        # Здесь можно реализовать более сложную логику анализа
        # На основе ключевых слов, тональности текста и т.д.
        
        title = news["title"].lower()
        votes = news.get("votes", {})
        positive = votes.get("positive", 0)
        negative = votes.get("negative", 0)
        
        # Анализ по голосам
        if positive > negative * 2:
            return "🟢 Позитивное"
        elif negative > positive * 2:
            return "🔴 Негативное"
        
        # Анализ по ключевым словам
        positive_words = ["bullish", "surge", "rally", "gain", "up", "high", "growth"]
        negative_words = ["bearish", "crash", "drop", "fall", "down", "low", "decline"]
        
        positive_count = sum(1 for word in positive_words if word in title)
        negative_count = sum(1 for word in negative_words if word in title)
        
        if positive_count > negative_count:
            return "🟢 Позитивное"
        elif negative_count > positive_count:
            return "🔴 Негативное"
        
        return "⚪️ Нейтральное"
        
    async def get_trending_topics(self) -> List[str]:
        """Получает трендовые темы."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "auth_token": self.api_key,
                    "kind": "stats",
                    "public": "true"
                }
                
                async with session.get(f"{self.base_url}/stats/", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("trending_topics", [])
                    else:
                        logger.error(f"Error fetching trending topics: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_trending_topics: {e}")
            return []
            
    async def get_news_by_currency(self, currency: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Получает новости по конкретной валюте."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "auth_token": self.api_key,
                    "currencies": currency,
                    "kind": "news",
                    "public": "true",
                    "published_after": (datetime.now() - timedelta(hours=hours)).isoformat()
                }
                
                async with session.get(f"{self.base_url}/posts/", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_news(data["results"])
                    else:
                        logger.error(f"Error fetching news for {currency}: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_news_by_currency: {e}")
            return []
            
    async def get_news_by_category(self, category: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Получает новости по категории."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "auth_token": self.api_key,
                    "categories": category,
                    "kind": "news",
                    "public": "true",
                    "published_after": (datetime.now() - timedelta(hours=hours)).isoformat()
                }
                
                async with session.get(f"{self.base_url}/posts/", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_news(data["results"])
                    else:
                        logger.error(f"Error fetching news for category {category}: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_news_by_category: {e}")
            return [] 