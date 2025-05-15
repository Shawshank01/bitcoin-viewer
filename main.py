# Entry point of this application

from network import get_bitcoin_nodes, connect_and_listen

if __name__ == "__main__":
    nodes = get_bitcoin_nodes()
    print("Found nodes:", nodes)

    if nodes:
        connect_and_listen(nodes, listen_duration=900)  # listen up to 15 minutes per node
    else:
        print("No nodes available.")