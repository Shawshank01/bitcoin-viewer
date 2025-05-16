import dns.resolver
import socket
import struct
import time
from utils import (
    double_sha256, format_timestamp, reverse_bytes,
    MAGIC_NUMBER, DEFAULT_PORT, BLOCK_HEADER_SIZE
)
from parser import parse_block, read_varint, read_bytes

def get_bitcoin_nodes(seed="dnsseed.bluematt.me"):
    """Get list of Bitcoin nodes from DNS seed."""
    try:
        result = dns.resolver.resolve(seed, 'A')
        return [ip.to_text() for ip in result]
    except Exception as e:
        print(f"DNS lookup failed: {e}")
        return []

def create_message(command, payload):
    """Create a Bitcoin protocol message."""
    command_bytes = command.encode() + b'\x00' * (12 - len(command))
    length = struct.pack('<I', len(payload))
    checksum = double_sha256(payload)[:4]
    return MAGIC_NUMBER + command_bytes + length + checksum + payload

def connect_and_handshake(ip, port=DEFAULT_PORT):
    """Connect to a Bitcoin node and perform handshake."""
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
        addr_recv_port = port
        addr_trans_services = 0
        addr_trans_ip = b"\x00" * 16
        addr_trans_port = port
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

        s.sendall(create_message('version', payload))
        print("Sent version message")

        # Read response from node
        def read_message(sock):
            header = sock.recv(24)
            if len(header) < 24:
                raise Exception("Incomplete header")
            magic, command, length, checksum = struct.unpack('<4s12sI4s', header)
            command = command.strip(b'\x00').decode()
            payload = b''
            while len(payload) < length:
                chunk = sock.recv(length - len(payload))
                if not chunk:
                    break
                payload += chunk
            return command, payload

        version_received = False
        verack_received = False

        while not (version_received and verack_received):
            command, payload = read_message(s)
            print(f"Received message: {command}")
            if command == "version":
                version_received = True
            elif command == "verack":
                verack_received = True

        s.sendall(create_message('verack', b''))
        print("Sent verack — handshake complete")
        return s
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def connect_and_listen(node_list, listen_duration=900):
    """Connect to nodes and listen for new blocks."""
    for ip in node_list:
        sock = connect_and_handshake(ip)
        if sock:
            sock.settimeout(30)
            print(f"Successfully connected to {ip}, listening for up to {listen_duration} seconds")
            start_time = time.time()
            
            def read_message(sock):
                header = sock.recv(24)
                if len(header) < 24:
                    raise Exception("Incomplete header")
                magic, command, length, checksum = struct.unpack('<4s12sI4s', header)
                command = command.strip(b'\x00').decode()
                payload = b''
                while len(payload) < length:
                    chunk = sock.recv(length - len(payload))
                    if not chunk:
                        break
                    payload += chunk
                return command, payload

            try:
                while time.time() - start_time < listen_duration:
                    try:
                        command, payload = read_message(sock)
                        if command == "inv":
                            count = payload[0]
                            print(f"Received 'inv' with {count} item(s)")
                            offset = 1
                            for _ in range(count):
                                if offset + 36 > len(payload):
                                    print("Truncated inv message")
                                    break
                                inv_type = struct.unpack('<I', payload[offset:offset+4])[0]
                                hash_hex = reverse_bytes(payload[offset+4:offset+36]).hex()
                                offset += 36
                                if inv_type == 2:  # Block
                                    print(f"New block announced with hash: {hash_hex}")
                                    
                                    # Request block data
                                    block_hash = bytes.fromhex(hash_hex)[::-1]
                                    getdata_payload = b'\x01' + struct.pack('<I', 2) + block_hash
                                    sock.sendall(create_message('getdata', getdata_payload))
                                    print("Sent getdata request for block")

                                    # Read and parse block
                                    resp_command, resp_payload = read_message(sock)
                                    if resp_command == "block":
                                        print(f"Received block message with {len(resp_payload)} bytes")
                                        try:
                                            block_info = parse_block(resp_payload)
                                            
                                            # Verify block hash
                                            computed_hash = double_sha256(resp_payload[:BLOCK_HEADER_SIZE])[::-1].hex()
                                            if computed_hash == hash_hex:
                                                print(f"✔ Verified block hash: {computed_hash}")
                                            else:
                                                print(f"✘ Block hash mismatch!")
                                                print(f"Expected: {hash_hex}")
                                                print(f"Computed: {computed_hash}")

                                            # Display block info
                                            header = block_info['header']
                                            print(f"Block Version: {header['version']}")
                                            print(f"Previous Block Hash: {reverse_bytes(header['prev_hash']).hex()}")
                                            print(f"Merkle Root: {reverse_bytes(header['merkle_root']).hex()}")
                                            print(f"Timestamp: {format_timestamp(header['timestamp'])} UTC")
                                            print(f"Bits: {header['bits']}")
                                            print(f"Nonce: {header['nonce']}")
                                            print(f"Transaction Count: {len(block_info['transactions'])}")

                                            # Display transactions
                                            MAX_PRINTED_TX = 10
                                            print(f"Displaying last {MAX_PRINTED_TX} transactions:")
                                            for tx in block_info['transactions'][-MAX_PRINTED_TX:]:
                                                print(f"Transaction: {tx['value']:.8f} BTC | TXID: {tx['txid']}")
                                        except Exception as e:
                                            print(f"Error parsing block: {e}")
                                    else:
                                        print(f"Unexpected response to getdata: {resp_command}")
                                    return
                    except socket.timeout:
                        continue
            except Exception as e:
                print(f"Error during listening: {e}")
            finally:
                sock.close()