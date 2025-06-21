import logging
import aiohttp
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import INVESTING_API_KEY
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MacroCalendar:
    """Сервис для работы с экономическим календарем."""
    
    def __init__(self):
        self.base_url = "https://api.forexfactory.com/v1"
        self.api_key = "YOUR_API_KEY"  # Замените на ваш API ключ
    
    async def get_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Получает экономические события на указанный период."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "api_key": self.api_key,
                    "from_date": datetime.now().strftime("%Y-%m-%d"),
                    "to_date": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                }
                
                async with session.get(f"{self.base_url}/calendar", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_events(data)
                    else:
                        logger.error(f"Error fetching events: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_events: {e}")
            return []
            
    def _process_events(self, events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Обрабатывает полученные события."""
        processed_events = []
        
        for event in events_data:
            # Определяем влияние события на крипторынок
            impact = self._analyze_impact(event)
            
            processed_events.append({
                "title": event["title"],
                "date": event["date"],
                "time": event["time"],
                "country": event["country"],
                "impact": impact["level"],
                "description": impact["description"],
                "forecast": event.get("forecast", "N/A"),
                "previous": event.get("previous", "N/A"),
                "actual": event.get("actual", "N/A"),
                "url": event.get("url", "")
            })
            
        return processed_events
        
    def _analyze_impact(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует влияние события на крипторынок."""
        impact = {
            "level": "low",
            "description": "Минимальное влияние на крипторынок"
        }
        
        # Ключевые слова для определения влияния
        high_impact = [
            "fed", "fomc", "interest rate", "powell",
            "inflation", "cpi", "gdp", "unemployment",
            "regulation", "crypto", "bitcoin", "blockchain"
        ]
        
        medium_impact = [
            "treasury", "bonds", "stocks", "forex",
            "trade", "retail", "manufacturing", "housing"
        ]
        
        # Проверяем заголовок и описание события
        event_text = f"{event['title']} {event.get('description', '')}".lower()
        
        # Подсчитываем количество ключевых слов
        high_count = sum(1 for word in high_impact if word in event_text)
        medium_count = sum(1 for word in medium_impact if word in event_text)
        
        # Определяем уровень влияния
        if high_count > 0:
            impact["level"] = "high"
            impact["description"] = "Сильное влияние на крипторынок"
        elif medium_count > 0:
            impact["level"] = "medium"
            impact["description"] = "Умеренное влияние на крипторынок"
            
        # Учитываем важность события из источника
        if event.get("importance", "").lower() == "high":
            impact["level"] = "high"
            
        return impact
        
    async def get_important_events(self) -> List[Dict[str, Any]]:
        """Получает важные события."""
        events = await self.get_events()
        return [event for event in events if event["impact"] == "high"]
        
    async def get_events_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Получает события по региону."""
        events = await self.get_events()
        return [event for event in events if event["country"].lower() == region.lower()]
        
    async def get_events_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Получает события на конкретную дату."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "api_key": self.api_key,
                    "date": date
                }
                
                async with session.get(f"{self.base_url}/calendar/date", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_events(data)
                    else:
                        logger.error(f"Error fetching events for date {date}: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_events_by_date: {e}")
            return []
            
    async def get_market_impact(self) -> Dict[str, Any]:
        """Анализирует влияние предстоящих событий на рынок."""
        events = await self.get_events(days=7)
        
        impact = {
            "overall": "neutral",
            "short_term": "neutral",
            "long_term": "neutral",
            "key_events": [],
            "recommendations": []
        }
        
        # Подсчитываем количество событий по важности
        high_impact = len([e for e in events if e["impact"] == "high"])
        medium_impact = len([e for e in events if e["impact"] == "medium"])
        
        # Определяем общее влияние
        total_weight = high_impact * 2 + medium_impact
        if total_weight > 5:
            impact["overall"] = "high volatility expected"
        elif total_weight > 2:
            impact["overall"] = "moderate volatility expected"
            
        # Выделяем ключевые события
        impact["key_events"] = [
            {
                "date": e["date"],
                "title": e["title"],
                "impact": e["impact"],
                "description": e["description"]
            }
            for e in events if e["impact"] == "high"
        ][:3]  # Топ-3 события
        
        # Формируем рекомендации
        if impact["overall"] == "high volatility expected":
            impact["recommendations"].append(
                "Рекомендуется повысить внимание к управлению рисками"
            )
        if high_impact > 0:
            impact["recommendations"].append(
                "Ожидается повышенная волатильность в даты важных событий"
            )
            
        return impact

    async def analyze_impact(self, event: dict) -> str:
        """Анализирует влияние события на рынок."""
        try:
            impact = ""
            
            # Анализ важности события
            if "FED" in event["event"] or "Interest Rate" in event["event"]:
                impact += "🔴 Критически важное событие\n"
            elif "GDP" in event["event"] or "NFP" in event["event"]:
                impact += "🟡 Важное событие\n"
            
            # Анализ фактического значения против прогноза
            if event["actual"] and event["forecast"]:
                actual = float(event["actual"].replace("%", ""))
                forecast = float(event["forecast"].replace("%", ""))
                
                if actual > forecast:
                    impact += "📈 Выше ожиданий - возможен рост\n"
                elif actual < forecast:
                    impact += "📉 Ниже ожиданий - возможно снижение\n"
                else:
                    impact += "➡️ Соответствует ожиданиям\n"
            
            return impact
            
        except Exception as e:
            logger.error(f"Error analyzing event impact: {e}")
            return "❓ Требуется ручной анализ"

    async def get_daily_summary(self) -> str:
        """Формирует ежедневную сводку важных событий."""
        try:
            events = await self.get_events(days=1)
            if not events:
                return "Нет важных событий на сегодня"
            
            summary = "📅 Важные экономические события:\n\n"
            
            for event in events:
                if event["importance"] in ["High", "Medium"]:
                    impact = await self.analyze_impact(event)
                    summary += f"🕒 {event['time']} - {event['country']}\n"
                    summary += f"📊 {event['event']}\n"
                    summary += f"📌 Факт: {event['actual']} | Прогноз: {event['forecast']}\n"
                    summary += f"🔄 Предыдущее: {event['previous']}\n"
                    summary += f"📝 Влияние:\n{impact}\n\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return "Ошибка при формировании сводки" 