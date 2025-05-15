# Entry point of this application

from network import get_bitcoin_nodes, connect_and_listen

if __name__ == "__main__":
    nodes = get_bitcoin_nodes()
    print("Found nodes:", nodes)

    if nodes:
        connect_and_listen(nodes)
    else:
        print("No nodes available.")