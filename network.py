import dns.resolver
import socket
import struct
import time
import hashlib

def get_bitcoin_nodes(seed="dnsseed.bluematt.me"):
    try:
        result = dns.resolver.resolve(seed, 'A')
        return [ip.to_text() for ip in result]
    except Exception as e:
        print(f"DNS lookup failed: {e}")
        return []

def connect_and_handshake(ip, port=8333):
    try:
        print(f"Connecting to {ip}:{port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((ip, port))

        # Build version payload
        version = 70015
        services = 0
        timestamp = int(time.time())
        addr_recv_services = 0
        addr_recv_ip = b"\x00" * 16
        addr_recv_port = 8333
        addr_trans_services = 0
        addr_trans_ip = b"\x00" * 16
        addr_trans_port = 8333
        nonce = 0
        user_agent_bytes = b'\x00'
        start_height = 0
        relay = 0

        payload = struct.pack('<iQQ', version, services, timestamp)
        payload += struct.pack('>Q16sH', addr_recv_services, addr_recv_ip, addr_recv_port)
        payload += struct.pack('>Q16sH', addr_trans_services, addr_trans_ip, addr_trans_port)
        payload += struct.pack('<Q', nonce)
        payload += user_agent_bytes
        payload += struct.pack('<i?', start_height, relay)

        # Bitcoin message
        magic = b'\xf9\xbe\xb4\xd9'
        command = b'version' + b'\x00' * (12 - len('version'))
        length = struct.pack('<I', len(payload))
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        message = magic + command + length + checksum + payload

        s.sendall(message)
        print("Sent version message")
        return s
    except Exception as e:
        print(f"Connection failed: {e}")
        return None