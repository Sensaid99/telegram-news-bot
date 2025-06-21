import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
import json

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Мокаем переменные окружения для тестов."""
    test_env = {
        'BOT_TOKEN': 'test_token',
        'CHANNEL_ID': '-1001234567890',
        'ETHERSCAN_API_KEY': 'test_etherscan_key',
        'BSCSCAN_API_KEY': 'test_bscscan_key',
        'SOLSCAN_API_KEY': 'test_solscan_key',
        'TRONGRID_API_KEY': 'test_trongrid_key',
        'INVESTING_API_KEY': 'test_investing_key',
        'BINANCE_API_KEY': 'test_binance_key',
        'BINANCE_API_SECRET': 'test_binance_secret',
        'TWELVEDATA_API_KEY': 'test_twelvedata_key'
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

class MockResponse:
    def __init__(self, data):
        self.data = data
        self.status = 200
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def json(self):
        return self.data

class MockSession:
    def __init__(self):
        self.closed = False
        
    async def close(self):
        self.closed = True
        
    def get(self, url, **kwargs):
        if 'blockchain.info' in url:
            return MockResponse(btc_data)
        elif 'etherscan.io' in url:
            return MockResponse(eth_data)
        elif 'bscscan.com' in url:
            return MockResponse(bsc_data)
        elif 'twelvedata.com' in url:
            return MockResponse(twelvedata_data)
        return MockResponse({})
        
    def post(self, url, **kwargs):
        if 'getRecentPerformanceSamples' in str(kwargs.get('json', {})):
            return MockResponse(sol_perf_data)
        elif 'getBlockTime' in str(kwargs.get('json', {})):
            return MockResponse(sol_block_data)
        elif 'getVoteAccounts' in str(kwargs.get('json', {})):
            return MockResponse(sol_validators_data)
        return MockResponse({})

# Bitcoin metrics
btc_data = {
    'n_tx': 300000,
    'n_unique_addresses': 1000000,
    'median_fee': 15.5
}

# Ethereum metrics
eth_data = {
    'status': '1',
    'result': {
        'SafeGasPrice': '25',
        'ProposeGasPrice': '30',
        'FastGasPrice': '35'
    }
}

# Solana metrics
sol_perf_data = {
    'result': [{
        'numTransactions': 24000,
        'numNonVoteTransactions': 12000,
        'samplePeriodSecs': 60
    }]
}

sol_block_data = {
    'result': int(1687286400)  # Example timestamp
}

sol_validators_data = {
    'result': {
        'current': [1] * 1000,
        'delinquent': [1] * 200
    }
}

# BSC metrics
bsc_data = {
    'status': '1',
    'result': {
        'SafeGasPrice': '3',
        'ProposeGasPrice': '4',
        'FastGasPrice': '5'
    }
}

# TwelveData metrics
twelvedata_data = {
    'values': [{
        'close': '100.50',
        'high': '101.50',
        'low': '99.50',
        'volume': '1000000',
        'percent_change': '2.5'
    }]
}

@pytest.fixture
async def mock_aiohttp_session():
    """Мокаем aiohttp.ClientSession для тестов."""
    mock_session = MockSession()
    with patch('aiohttp.ClientSession', return_value=mock_session):
        yield mock_session 