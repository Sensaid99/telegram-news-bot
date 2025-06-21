import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class InvestingData:
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_timeout = timedelta(minutes=5)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        cache_time, _ = self.cache[key]
        return datetime.now() - cache_time < self.cache_timeout

    async def get_market_data(self) -> Dict[str, float]:
        """Получает основные рыночные данные с investing.com"""
        try:
            await self._ensure_session()
            
            if self._is_cache_valid('market_data'):
                return self.cache['market_data'][1]

            # URLs для основных индикаторов
            urls = {
                'commodities': 'https://www.investing.com/commodities/',
                'indices': 'https://www.investing.com/indices/',
                'bonds': 'https://www.investing.com/rates-bonds/',
                'currencies': 'https://www.investing.com/currencies/'
            }

            tasks = []
            for category, url in urls.items():
                tasks.append(self._fetch_page(url))

            pages = await asyncio.gather(*tasks, return_exceptions=True)

            data = {}
            
            for page, (category, _) in zip(pages, urls.items()):
                if isinstance(page, Exception):
                    logger.error(f"Error fetching {category}: {page}")
                    continue
                    
                if category == 'commodities':
                    data.update(self._parse_commodities(page))
                elif category == 'indices':
                    data.update(self._parse_indices(page))
                elif category == 'bonds':
                    data.update(self._parse_bonds(page))
                elif category == 'currencies':
                    data.update(self._parse_currencies(page))

            self.cache['market_data'] = (datetime.now(), data)
            return data

        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}

    async def _fetch_page(self, url: str) -> str:
        """Получает HTML-страницу по URL"""
        try:
            async with self.session.get(url, timeout=10) as response:
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise

    def _parse_commodities(self, html: str) -> Dict[str, float]:
        """Парсит данные по сырьевым товарам"""
        data = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'cross_rate_1'})
            
            if table:
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        name = cells[1].text.strip()
                        price_text = cells[2].text.strip().replace(',', '')
                        
                        if name == 'Brent Oil':
                            try:
                                data['brent'] = float(price_text)
                            except ValueError:
                                pass
                        elif name == 'Crude Oil WTI':
                            try:
                                data['wti'] = float(price_text)
                            except ValueError:
                                pass

        except Exception as e:
            logger.error(f"Error parsing commodities: {e}")
        
        return data

    def _parse_indices(self, html: str) -> Dict[str, float]:
        """Парсит данные по индексам"""
        data = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'cross_rate_1'})
            
            if table:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        name = cells[1].text.strip()
                        price_text = cells[2].text.strip().replace(',', '')
                        
                        if name == 'Dow Jones':
                            try:
                                data['dow'] = float(price_text)
                            except ValueError:
                                pass
                        elif name == 'Nasdaq':
                            try:
                                data['nasdaq'] = float(price_text)
                            except ValueError:
                                pass

        except Exception as e:
            logger.error(f"Error parsing indices: {e}")
        
        return data

    def _parse_bonds(self, html: str) -> Dict[str, float]:
        """Парсит данные по облигациям"""
        data = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'cross_rate_1'})
            
            if table:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        name = cells[1].text.strip()
                        price_text = cells[2].text.strip().replace(',', '')
                        
                        if 'U.S. 10Y' in name:
                            try:
                                data['us_10y'] = float(price_text)
                            except ValueError:
                                pass
                        elif 'Germany 10Y' in name:
                            try:
                                data['de_10y'] = float(price_text)
                            except ValueError:
                                pass

        except Exception as e:
            logger.error(f"Error parsing bonds: {e}")
        
        return data

    def _parse_currencies(self, html: str) -> Dict[str, float]:
        """Парсит данные по валютным парам"""
        data = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'cross_rate_1'})
            
            if table:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        name = cells[1].text.strip()
                        price_text = cells[2].text.strip().replace(',', '')
                        
                        if name == 'EUR/USD':
                            try:
                                data['eurusd'] = float(price_text)
                            except ValueError:
                                pass
                        elif name == 'GBP/USD':
                            try:
                                data['gbpusd'] = float(price_text)
                            except ValueError:
                                pass
                        elif name == 'USD/JPY':
                            try:
                                data['usdjpy'] = float(price_text)
                            except ValueError:
                                pass

        except Exception as e:
            logger.error(f"Error parsing currencies: {e}")
        
        return data

investing_data = InvestingData() 