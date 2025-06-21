import logging
from typing import Dict, List, Tuple, Any
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarketAnalysis:
    """Класс для расширенного анализа рыночных данных и корреляций."""
    
    def __init__(self):
        self.market_state = "NEUTRAL"  # BULLISH, NEUTRAL, BEARISH
        self.risk_level = "MEDIUM"     # LOW, MEDIUM, HIGH
        
    def analyze_dxy(self, current: float, previous: float) -> Dict[str, Any]:
        """Анализ индекса доллара DXY и его влияния"""
        change = ((current - previous) / previous * 100) if previous else 0
        trend = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        
        analysis = {
            'value': current,
            'change': change,
            'trend': trend,
            'strength': 'сильный' if current > 103 else 'слабый' if current < 97 else 'нейтральный',
            'impact': """
• Сильный доллар (DXY > 103) обычно негативен для крипторынка
• Слабый доллар (DXY < 97) часто приводит к росту криптовалют
• Резкий рост DXY может вызвать отток капитала из рисковых активов
            """.strip()
        }
        return analysis
        
    def analyze_sp500(self, current: float, previous: float) -> Dict[str, Any]:
        """Анализ индекса S&P 500 и корреляции с криптовалютами"""
        change = ((current - previous) / previous * 100) if previous else 0
        trend = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        
        analysis = {
            'value': current,
            'change': change,
            'trend': trend,
            'state': 'бычий' if current > previous else 'медвежий' if current < previous else 'боковой',
            'correlation': """
• Высокая корреляция с BTC (> 0.6) в периоды рыночного стресса
• Технологический сектор S&P 500 имеет наибольшую корреляцию
• Падение S&P 500 часто приводит к распродажам на крипторынке
            """.strip()
        }
        return analysis
        
    def analyze_vix(self, current: float, previous: float) -> Dict[str, Any]:
        """Анализ индекса волатильности VIX"""
        change = ((current - previous) / previous * 100) if previous else 0
        trend = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        
        analysis = {
            'value': current,
            'change': change,
            'trend': trend,
            'risk_level': 'высокий' if current > 30 else 'низкий' if current < 15 else 'средний',
            'interpretation': """
• VIX > 30: Высокая волатильность, возможна паника на рынке
• VIX < 15: Низкая волатильность, рынок спокоен
• Резкий рост VIX часто предшествует коррекции на крипторынке
            """.strip()
        }
        return analysis
        
    def analyze_gold(self, current: float, previous: float) -> Dict[str, Any]:
        """Анализ цены на золото и корреляции с BTC"""
        change = ((current - previous) / previous * 100) if previous else 0
        trend = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        
        analysis = {
            'value': current,
            'change': change,
            'trend': trend,
            'correlation': """
• BTC и золото часто растут вместе при высокой инфляции
• Золото - традиционный защитный актив
• В периоды кризиса корреляция BTC и золота может усиливаться
            """.strip()
        }
        return analysis
        
    def analyze_nasdaq(self, current: float, previous: float) -> Dict[str, Any]:
        """Анализ индекса NASDAQ и его влияния на крипторынок"""
        change = ((current - previous) / previous * 100) if previous else 0
        trend = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        
        analysis = {
            'value': current,
            'change': change,
            'trend': trend,
            'correlation': """
• Сильная корреляция с BTC (> 0.7) из-за технологического фокуса
• Опережающий индикатор для крипторынка
• Настроения в технологическом секторе влияют на криптовалюты
            """.strip()
        }
        return analysis
        
    def analyze_treasuries(self, y10: float, y2: float, prev_y10: float, prev_y2: float) -> Dict[str, Any]:
        """Анализ доходности трежерис и кривой доходности"""
        spread = y10 - y2
        prev_spread = prev_y10 - prev_y2
        spread_change = spread - prev_spread
        
        analysis = {
            'y10': y10,
            'y2': y2,
            'spread': spread,
            'trend': "↗️" if spread_change > 0 else "↘️" if spread_change < 0 else "→",
            'state': 'нормальная' if spread > 0 else 'инвертированная',
            'interpretation': """
• Инверсия кривой (спред < 0) - сигнал рецессии
• Рост доходностей негативен для рисковых активов
• Снижение доходностей может поддержать крипторынок
            """.strip()
        }
        return analysis
        
    def analyze_crude_oil(self, current: float, previous: float) -> Dict[str, Any]:
        """Анализ цен на нефть и влияния на инфляцию"""
        change = ((current - previous) / previous * 100) if previous else 0
        trend = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        
        analysis = {
            'value': current,
            'change': change,
            'trend': trend,
            'impact': """
• Рост цен на нефть усиливает инфляционное давление
• Высокие цены могут привести к ужесточению политики ЦБ
• Нефть влияет на глобальные потоки капитала
            """.strip()
        }
        return analysis
        
    def analyze_rates(self, rates: Dict[str, float]) -> Dict[str, Any]:
        """Анализ процентных ставок и их влияния"""
        fed_rate = rates.get('fed', 0)
        
        analysis = {
            'rates': rates,
            'environment': 'ужесточение' if fed_rate > 4 else 'нейтральный' if fed_rate > 2 else 'мягкий',
            'impact': """
• Высокие ставки (>4%) негативны для рисковых активов
• Ожидание снижения ставок обычно позитивно для крипторынка
• Разница ставок влияет на глобальные потоки капитала
            """.strip()
        }
        return analysis
        
    @staticmethod
    def get_market_state(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует состояние рынка на основе метрик."""
        try:
            bullish_factors = 0
            bearish_factors = 0
            
            # Анализ DXY
            if metrics['dxy'] < metrics.get('prev_dxy', float('inf')):
                bullish_factors += 1
            else:
                bearish_factors += 1
                
            # Анализ S&P 500
            if metrics['sp500'] > metrics.get('prev_sp500', 0):
                bullish_factors += 1
            else:
                bearish_factors += 1
                
            # Анализ VIX
            if metrics['vix'] < 20:
                bullish_factors += 1
            elif metrics['vix'] > 30:
                bearish_factors += 1
                
            # Анализ Gold
            if metrics['gold'] > metrics.get('prev_gold', 0):
                bearish_factors += 1
            else:
                bullish_factors += 1
                
            # Определение индикатора
            if bullish_factors > bearish_factors:
                indicator = "🟢 Бычий"
            elif bearish_factors > bullish_factors:
                indicator = "🔴 Медвежий"
            else:
                indicator = "⚪️ Нейтральный"
                
            return {
                'indicator': indicator,
                'bullish_factors': bullish_factors,
                'bearish_factors': bearish_factors
            }
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return {
                'indicator': "⚠️ Ошибка анализа",
                'bullish_factors': 0,
                'bearish_factors': 0
            }

# Create instance
market_analysis = MarketAnalysis() 