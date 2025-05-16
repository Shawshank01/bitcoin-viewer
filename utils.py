# Helper functions

import hashlib
import struct
from datetime import datetime, timezone

# Constants
BLOCK_HEADER_SIZE = 80
MAGIC_NUMBER = b'\xf9\xbe\xb4\xd9'
DEFAULT_PORT = 8333

def double_sha256(data):
    """Calculate double SHA256 hash of data."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def format_timestamp(timestamp):
    """Format Unix timestamp to human-readable UTC time."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def reverse_bytes(data):
    """Reverse byte order of data."""
    return data[::-1]

def satoshi_to_btc(satoshi):
    """Convert satoshi amount to BTC."""
    return satoshi / 1e8

