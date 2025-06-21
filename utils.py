from typing import Dict, List, Optional
from datetime import datetime
import json
import os

def load_template(template_name: str) -> str:
    """Load message template from file."""
    template_path = os.path.join('templates', f'{template_name}.txt')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def format_price(price: float) -> str:
    """Format price with appropriate precision."""
    if price < 0.01:
        return f"${price:.6f}"
    elif price < 1:
        return f"${price:.4f}"
    elif price < 100:
        return f"${price:.2f}"
    else:
        return f"${price:,.2f}"

def format_volume(volume: float) -> str:
    """Format volume with appropriate suffix."""
    if volume >= 1_000_000_000:
        return f"${volume/1_000_000_000:.1f}B"
    elif volume >= 1_000_000:
        return f"${volume/1_000_000:.1f}M"
    else:
        return f"${volume:,.0f}"

def format_change(change: float) -> str:
    """Format price change with color emoji."""
    if change > 0:
        return f"🟢 {change:+.1f}%"
    elif change < 0:
        return f"🔴 {change:+.1f}%"
    else:
        return f"⚪️ {change:+.1f}%"

def save_to_cache(key: str, data: Dict, expire_minutes: int = 5):
    """Save data to local cache file."""
    cache_dir = 'cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        
    cache_file = os.path.join(cache_dir, f'{key}.json')
    data['expires_at'] = datetime.utcnow().timestamp() + (expire_minutes * 60)
    
    with open(cache_file, 'w') as f:
        json.dump(data, f)

def load_from_cache(key: str) -> Optional[Dict]:
    """Load data from local cache if not expired."""
    cache_file = os.path.join('cache', f'{key}.json')
    
    if not os.path.exists(cache_file):
        return None
        
    with open(cache_file, 'r') as f:
        data = json.load(f)
        
    if datetime.utcnow().timestamp() > data.get('expires_at', 0):
        return None
        
    return data

def truncate_text(text: str, max_length: int = 4096) -> str:
    """Truncate text to fit Telegram message limits."""
    if len(text) <= max_length:
        return text
        
    return text[:max_length-3] + "..." 