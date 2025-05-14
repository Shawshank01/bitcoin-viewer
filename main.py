# Entry point of this application

from network import get_bitcoin_nodes, connect_and_handshake

if __name__ == "__main__":
    nodes = get_bitcoin_nodes()
    print("Found nodes:", nodes)

    for ip in nodes:
        s = connect_and_handshake(ip)
        if s:
            print(f"Successfully connected to {ip}")
            break
    else:
        print("All connection attempts failed.")