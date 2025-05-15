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

        # Send our verack
        magic = b'\xf9\xbe\xb4\xd9'
        command = b'verack' + b'\x00' * (12 - len('verack'))
        payload = b''
        length = struct.pack('<I', 0)
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        message = magic + command + length + checksum + payload
        s.sendall(message)
        print("Sent verack — handshake complete")
        return s
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


# Connect to each node, handshake, and briefly listen for inv messages
def connect_and_listen(node_list, listen_duration=300):
    import time
    for ip in node_list:
        sock = connect_and_handshake(ip)
        if sock:
            print(f"Successfully connected to {ip}, listening for up to {listen_duration} seconds")
            start_time = time.time()
            def read_message(sock):
                sock.settimeout(30)
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
                                hash_hex = payload[offset+4:offset+36][::-1].hex()
                                offset += 36
                                if inv_type == 2:
                                    print(f"New block announced with hash: {hash_hex}")

                                    # Construct and send getdata message
                                    block_hash = bytes.fromhex(hash_hex)[::-1]
                                    count_bytes = b'\x01'
                                    inv_type_bytes = struct.pack('<I', 2)
                                    getdata_payload = count_bytes + inv_type_bytes + block_hash

                                    magic = b'\xf9\xbe\xb4\xd9'
                                    cmd_bytes = b'getdata' + b'\x00' * (12 - len('getdata'))
                                    length = struct.pack('<I', len(getdata_payload))
                                    checksum = hashlib.sha256(hashlib.sha256(getdata_payload).digest()).digest()[:4]
                                    message = magic + cmd_bytes + length + checksum + getdata_payload
                                    sock.sendall(message)
                                    print("Sent getdata request for block")

                                    # Read block response
                                    resp_command, resp_payload = read_message(sock)
                                    if resp_command == "block":
                                        print(f"Received block message with {len(resp_payload)} bytes")
                                    else:
                                        print(f"Unexpected response to getdata: {resp_command}")
                                    return
                    except socket.timeout:
                        continue  # try again until total listen_duration is exceeded
                    except Exception as e:
                        print(f"Error reading from {ip}: {e}")
                        break
            finally:
                sock.close()
    print("No block announcements received from any nodes.")