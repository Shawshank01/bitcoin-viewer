# Code to parse Bitcoin protocol messages

import struct
from utils import double_sha256, BLOCK_HEADER_SIZE, satoshi_to_btc

def read_varint(data, offset):
    """Read a variable length integer from the data."""
    first = data[offset]
    if first < 0xfd:
        return first, offset + 1
    elif first == 0xfd:
        return struct.unpack('<H', data[offset+1:offset+3])[0], offset + 3
    elif first == 0xfe:
        return struct.unpack('<I', data[offset+1:offset+5])[0], offset + 5
    else:
        return struct.unpack('<Q', data[offset+1:offset+9])[0], offset + 9

def read_bytes(data, offset, length):
    """Read a fixed number of bytes from the data."""
    return data[offset:offset+length], offset + length

def parse_block_header(header):
    """Parse a Bitcoin block header."""
    version, prev_hash, merkle_root, timestamp, bits, nonce = struct.unpack('<I32s32sIII', header)
    return {
        'version': version,
        'prev_hash': prev_hash,
        'merkle_root': merkle_root,
        'timestamp': timestamp,
        'bits': bits,
        'nonce': nonce
    }

def parse_transaction(data, offset):
    """Parse a Bitcoin transaction."""
    tx_start = offset
    
    # Version
    _, offset = read_bytes(data, offset, 4)
    
    # Input count and inputs
    in_count, offset = read_varint(data, offset)
    for _ in range(in_count):
        _, offset = read_bytes(data, offset, 36)  # prev txid + index
        script_len, offset = read_varint(data, offset)
        _, offset = read_bytes(data, offset, script_len + 4)  # script + sequence
    
    # Output count and outputs
    out_count, offset = read_varint(data, offset)
    total_output = 0
    for _ in range(out_count):
        value_bytes, offset = read_bytes(data, offset, 8)
        value = struct.unpack('<Q', value_bytes)[0]
        total_output += value
        script_len, offset = read_varint(data, offset)
        _, offset = read_bytes(data, offset, script_len)
    
    # Lock time
    _, offset = read_bytes(data, offset, 4)
    
    # Calculate transaction ID
    tx_raw = data[tx_start:offset]
    txid = double_sha256(tx_raw)[::-1].hex()
    
    return {
        'txid': txid,
        'value': satoshi_to_btc(total_output),
        'offset': offset
    }

def parse_block(data):
    """Parse a complete Bitcoin block."""
    if len(data) < BLOCK_HEADER_SIZE:
        raise ValueError("Block data too short")
    
    # Parse header
    header = data[:BLOCK_HEADER_SIZE]
    header_info = parse_block_header(header)
    
    # Parse transactions
    tx_count, offset = read_varint(data, BLOCK_HEADER_SIZE)
    transactions = []
    
    for _ in range(tx_count):
        tx_info = parse_transaction(data, offset)
        transactions.append(tx_info)
        offset = tx_info['offset']
    
    return {
        'header': header_info,
        'transactions': transactions
    }

