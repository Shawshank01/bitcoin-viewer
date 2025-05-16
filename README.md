# Bitcoin Blockchain Viewer

This project is a simplified Bitcoin blockchain viewer that connects directly to the Bitcoin peer-to-peer (P2P) network, receives block broadcasts in real time, and displays useful information about each new block.

## Features

- Connects to live Bitcoin nodes using DNS seeds
- Listens for `inv` messages announcing new blocks
- Sends `getdata` requests to fetch full block details
- Parses and displays:
  - Block version
  - Block timestamp (human-readable UTC)
  - Previous block hash
  - Merkle root
  - Nonce and difficulty (bits)
  - Total transaction count
  - Last 10 transactions with BTC value and TXID
- Verifies block hash from the block header
- Modular parsing logic using `parser.py`
- Automatic reconnection to different nodes if connection fails

## Requirements

- Python 3.8+
- Internet connection (for connecting to live Bitcoin nodes)
- dnspython (for DNS resolution)

## Installation

Clone this repository and set up a virtual environment:

```bash
git clone https://github.com/yourusername/bitcoin-viewer.git
cd bitcoin-viewer
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

The script will:
- Resolve Bitcoin node IPs from DNS seed
- Connect to nodes in sequence (with 10-second connection timeout)
- Listen for new blocks for 15 minutes (900 seconds) by default
- Display each block's header and selected transactions when new blocks are mined
- Automatically try the next node if connection fails
- Verify block hashes to ensure data integrity

### Example Output

When a new block is found, the script will display:
```
New block announced with hash: [block_hash]
Sent getdata request for block
Received block message with [size] bytes
✔ Verified block hash: [block_hash]
Block Version: [version]
Previous Block Hash: [prev_hash]
Merkle Root: [merkle_root]
Timestamp: [timestamp] UTC
Bits: [bits]
Nonce: [nonce]
Transaction Count: [count]
Displaying last 10 transactions:
Transaction: [amount] BTC | TXID: [txid]
...
```

## File Structure

- `main.py`: Entry point for the app
- `network.py`: Handles P2P communication and block processing loop
- `parser.py`: Contains reusable functions to parse headers, transactions, and Bitcoin message components
- `utils.py`: Helper functions for hashing, timestamp formatting, and unit conversion
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation

## Dependencies

- dnspython: For DNS resolution of Bitcoin nodes
- (Other dependencies will be listed in requirements.txt)