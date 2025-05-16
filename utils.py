# Helper functions for Bitcoin protocol operations

import hashlib
from datetime import datetime, timezone

# Bitcoin protocol constants
BLOCK_HEADER_SIZE = 80  # Size of a Bitcoin block header in bytes
MAGIC_NUMBER = b'\xf9\xbe\xb4\xd9'  # Bitcoin network magic number
DEFAULT_PORT = 8333  # Default Bitcoin P2P port

def double_sha256(data):
    """Calculate double SHA256 hash of data."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def format_timestamp(timestamp):
    """Format Unix timestamp to human-readable UTC time."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def reverse_bytes(data):
    """Reverse byte order of data (little-endian to big-endian or vice versa)."""
    return data[::-1]

def satoshi_to_btc(satoshi):
    """Convert satoshi amount to BTC (1 BTC = 100,000,000 satoshis)."""
    return satoshi / 1e8

