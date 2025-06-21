import pytest
import asyncio
from services.blockchain_stats import BlockchainStats
from services.macro_data import MacroData

@pytest.fixture
async def blockchain_stats(mock_aiohttp_session):
    """Фикстура для BlockchainStats с моками."""
    stats = BlockchainStats()
    try:
        yield stats
    finally:
        await stats.close()

@pytest.fixture
async def macro_data(mock_aiohttp_session):
    """Фикстура для MacroData с моками."""
    data = MacroData()
    try:
        yield data
    finally:
        await data.close()

@pytest.mark.asyncio
async def test_solana_metrics(blockchain_stats):
    """Тест получения метрик Solana."""
    metrics = await blockchain_stats.get_solana_metrics()
    assert metrics is not None
    assert 'tps' in metrics
    assert 'fee' in metrics
    assert 'validators' in metrics
    assert 'block_time' in metrics
    assert isinstance(metrics['tps'], float)
    assert isinstance(metrics['fee'], float)
    assert isinstance(metrics['validators'], int)
    assert isinstance(metrics['block_time'], (int, float))
    assert metrics['tps'] == 400.0  # 24000/60
    assert metrics['fee'] == 200.0  # 12000/60
    assert metrics['validators'] == 1200  # 1000 + 200
    assert metrics['block_time'] == 1687286400

@pytest.mark.asyncio
async def test_network_stats_formatting(blockchain_stats):
    """Тест форматирования сетевой статистики."""
    stats = await blockchain_stats.get_network_stats()
    assert isinstance(stats, str)
    assert "Bitcoin:" in stats
    assert "300,000" in stats  # Transactions
    assert "1,000,000" in stats  # Active addresses
    assert "15.5" in stats  # Fee
    assert "Ethereum:" in stats
    assert "25.00" in stats  # Gas
    assert "BSC:" in stats
    assert "3.0" in stats  # Gas
    assert "Solana:" in stats
    assert "400.0" in stats  # TPS
    assert "200.00" in stats  # Fee
    assert "1,200" in stats  # Validators

@pytest.mark.asyncio
async def test_macro_indicators(macro_data):
    """Тест получения макроэкономических индикаторов."""
    for symbol in macro_data.symbols.keys():
        data = await macro_data.get_indicator_data(symbol)
        assert data is not None
        assert 'price' in data
        assert 'change' in data
        assert 'volume' in data
        assert isinstance(data['price'], float)
        assert isinstance(data['change'], float)
        assert isinstance(data['volume'], float)
        assert data['price'] == 100.50
        assert data['change'] == 2.5
        assert data['volume'] == 1000000.0
        assert data['high'] == 101.50
        assert data['low'] == 99.50

@pytest.mark.asyncio
async def test_market_indicators_formatting(macro_data):
    """Тест форматирования рыночных индикаторов."""
    indicators = await macro_data.get_market_indicators()
    assert isinstance(indicators, str)
    assert "Vol:" in indicators
    for symbol in macro_data.symbols.keys():
        assert symbol in indicators or (symbol == 'GC' and "Gold:" in indicators)
    assert "100.50" in indicators
    assert "+2.5%" in indicators
    assert "1.0M" in indicators

@pytest.mark.asyncio
async def test_detailed_report_formatting(macro_data):
    """Тест форматирования детального отчета."""
    report = await macro_data.get_detailed_report()
    assert isinstance(report, str)
    assert "US Dollar Index" in report
    assert "S&P 500 Index" in report
    assert "CBOE Volatility Index" in report
    assert "Gold ETF" in report
    assert "Объем:" in report
    assert "100.50" in report
    assert "+2.5%" in report
    assert "1.0M" in report
    assert "99.50 - 101.50" in report 