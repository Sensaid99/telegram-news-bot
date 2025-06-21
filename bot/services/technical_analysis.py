import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Tuple
from .binance import BinanceService

logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    """Сервис технического анализа."""
    
    def __init__(self):
        self.binance = BinanceService()
        
    async def get_analysis(self, symbol: str, interval: str = "1h") -> Dict[str, Any]:
        """Получает технический анализ для монеты."""
        try:
            # Получаем исторические данные
            klines = await self.binance.get_klines(symbol, interval, limit=100)
            df = self._prepare_dataframe(klines)
            
            # Рассчитываем индикаторы
            indicators = self._calculate_indicators(df)
            
            # Определяем паттерны
            patterns = self._find_patterns(df)
            
            # Определяем уровни
            levels = self._find_levels(df)
            
            # Формируем сигналы
            signals = self._generate_signals(df, indicators, patterns, levels)
            
            return {
                "indicators": indicators,
                "patterns": patterns,
                "levels": levels,
                "signals": signals,
                "trend": self._determine_trend(df, indicators)
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {}
            
    def _prepare_dataframe(self, klines: List[List[Any]]) -> pd.DataFrame:
        """Подготавливает DataFrame для анализа."""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
            'taker_buy_quote_volume', 'ignore'
        ])
        
        # Конвертируем типы
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
        
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Рассчитывает технические индикаторы."""
        indicators = {}
        
        # Скользящие средние
        indicators['sma_20'] = df['close'].rolling(window=20).mean().iloc[-1]
        indicators['sma_50'] = df['close'].rolling(window=50).mean().iloc[-1]
        indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1]
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        indicators['macd'] = macd.iloc[-1]
        indicators['macd_signal'] = signal.iloc[-1]
        indicators['macd_hist'] = macd.iloc[-1] - signal.iloc[-1]
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Bollinger Bands
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        indicators['bb_upper'] = sma_20.iloc[-1] + (std_20.iloc[-1] * 2)
        indicators['bb_lower'] = sma_20.iloc[-1] - (std_20.iloc[-1] * 2)
        indicators['bb_middle'] = sma_20.iloc[-1]
        
        # Stochastic
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        k = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        indicators['stoch_k'] = k.iloc[-1]
        indicators['stoch_d'] = k.rolling(window=3).mean().iloc[-1]
        
        return indicators
        
    def _find_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Находит технические паттерны."""
        patterns = []
        
        # Doji
        body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        wick = df['high'].iloc[-1] - df['low'].iloc[-1]
        if body < (wick * 0.1):
            patterns.append({
                "name": "Doji",
                "type": "neutral",
                "reliability": "high"
            })
            
        # Hammer
        body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        upper_wick = df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])
        lower_wick = min(df['open'].iloc[-1], df['close'].iloc[-1]) - df['low'].iloc[-1]
        if (lower_wick > (body * 2)) and (upper_wick < (body * 0.5)):
            patterns.append({
                "name": "Hammer",
                "type": "bullish",
                "reliability": "medium"
            })
            
        # Engulfing
        prev_body = abs(df['close'].iloc[-2] - df['open'].iloc[-2])
        curr_body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        if curr_body > prev_body:
            if (df['close'].iloc[-1] > df['open'].iloc[-1]) and (df['close'].iloc[-2] < df['open'].iloc[-2]):
                patterns.append({
                    "name": "Bullish Engulfing",
                    "type": "bullish",
                    "reliability": "high"
                })
            elif (df['close'].iloc[-1] < df['open'].iloc[-1]) and (df['close'].iloc[-2] > df['open'].iloc[-2]):
                patterns.append({
                    "name": "Bearish Engulfing",
                    "type": "bearish",
                    "reliability": "high"
                })
                
        return patterns
        
    def _find_levels(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Находит уровни поддержки и сопротивления."""
        levels = {
            "support": [],
            "resistance": []
        }
        
        # Находим локальные минимумы и максимумы
        for i in range(2, len(df) - 2):
            # Поддержка
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                df['low'].iloc[i] < df['low'].iloc[i-2] and
                df['low'].iloc[i] < df['low'].iloc[i+1] and
                df['low'].iloc[i] < df['low'].iloc[i+2]):
                levels["support"].append(df['low'].iloc[i])
                
            # Сопротивление
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and
                df['high'].iloc[i] > df['high'].iloc[i-2] and
                df['high'].iloc[i] > df['high'].iloc[i+1] and
                df['high'].iloc[i] > df['high'].iloc[i+2]):
                levels["resistance"].append(df['high'].iloc[i])
                
        # Оставляем только значимые уровни
        support_levels = sorted(list(set([round(x, 2) for x in levels["support"]])))
        resistance_levels = sorted(list(set([round(x, 2) for x in levels["resistance"]])))
        
        levels["support"] = support_levels[-3:] if len(support_levels) >= 3 else support_levels
        levels["resistance"] = resistance_levels[:3] if len(resistance_levels) >= 3 else resistance_levels
        
        return levels
        
    def _generate_signals(self, df: pd.DataFrame, indicators: Dict[str, Any],
                         patterns: List[Dict[str, Any]], levels: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Генерирует торговые сигналы."""
        signals = []
        current_price = df['close'].iloc[-1]
        
        # Сигналы по индикаторам
        if indicators['macd'] > indicators['macd_signal']:
            signals.append({
                "type": "MACD",
                "signal": "buy",
                "strength": "medium",
                "description": "MACD пересек сигнальную линию снизу вверх"
            })
            
        if indicators['rsi'] < 30:
            signals.append({
                "type": "RSI",
                "signal": "buy",
                "strength": "strong",
                "description": "RSI указывает на перепроданность"
            })
        elif indicators['rsi'] > 70:
            signals.append({
                "type": "RSI",
                "signal": "sell",
                "strength": "strong",
                "description": "RSI указывает на перекупленность"
            })
            
        if current_price < indicators['bb_lower']:
            signals.append({
                "type": "Bollinger Bands",
                "signal": "buy",
                "strength": "medium",
                "description": "Цена ниже нижней полосы Боллинджера"
            })
        elif current_price > indicators['bb_upper']:
            signals.append({
                "type": "Bollinger Bands",
                "signal": "sell",
                "strength": "medium",
                "description": "Цена выше верхней полосы Боллинджера"
            })
            
        # Сигналы по паттернам
        for pattern in patterns:
            signals.append({
                "type": "Pattern",
                "signal": "buy" if pattern['type'] == "bullish" else "sell",
                "strength": "high" if pattern['reliability'] == "high" else "medium",
                "description": f"Обнаружен паттерн {pattern['name']}"
            })
            
        # Сигналы по уровням
        for support in levels['support']:
            if abs(current_price - support) / current_price < 0.01:  # В пределах 1%
                signals.append({
                    "type": "Support",
                    "signal": "buy",
                    "strength": "strong",
                    "description": f"Цена на уровне поддержки {support:.2f}"
                })
                
        for resistance in levels['resistance']:
            if abs(current_price - resistance) / current_price < 0.01:  # В пределах 1%
                signals.append({
                    "type": "Resistance",
                    "signal": "sell",
                    "strength": "strong",
                    "description": f"Цена на уровне сопротивления {resistance:.2f}"
                })
                
        return signals
        
    def _determine_trend(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> str:
        """Определяет текущий тренд."""
        # Анализируем несколько факторов для определения тренда
        
        factors = 0
        
        # MA тренд
        if indicators['sma_20'] > indicators['sma_50']:
            factors += 1
        else:
            factors -= 1
            
        # MACD тренд
        if indicators['macd'] > 0:
            factors += 1
        else:
            factors -= 1
            
        # RSI тренд
        if indicators['rsi'] > 50:
            factors += 1
        else:
            factors -= 1
            
        # Цена относительно BB
        if df['close'].iloc[-1] > indicators['bb_middle']:
            factors += 1
        else:
            factors -= 1
            
        if factors >= 2:
            return "🟢 Восходящий"
        elif factors <= -2:
            return "🔴 Нисходящий"
        else:
            return "⚪️ Боковой" 