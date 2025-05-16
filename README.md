# Bitcoin Blockchain Viewer

This project is a simplified Bitcoin blockchain viewer that connects directly to the Bitcoin peer-to-peer (P2P) network, receives block broadcasts in real time, and displays useful information about each new block.

## Features

- Connects to live Bitcoin nodes using DNS seeds
- Listens for `inv` messages announcing new blocks
- Sends `getdata` requests to fetch full block details
- Parses and displays:
  - Block timestamp (human-readable UTC)
  - Nonce and difficulty (bits)
  - Total transaction count
  - Last 10 transactions with BTC value and TXID
- Verifies block hash from the block header
- Modular parsing logic using `parser.py`

## Requirements

- Python 3.8+
- Internet connection (for connecting to live Bitcoin nodes)

## Installation

Clone this repository and set up a virtual environment:

```bash
git clone https://github.com/yourusername/bitcoin-viewer.git
cd bitcoin-viewer
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt  # If applicable
```

## Usage

Run the application:

```bash
python main.py
```

The script will:
- Resolve Bitcoin node IPs from DNS seed
- Connect to nodes in sequence
- Display each block's header and selected transactions when new blocks are mined

## File Structure

- `main.py`: Entry point for the app
- `network.py`: Handles P2P communication and block processing loop
- `parser.py`: Contains reusable functions to parse headers, transactions, and Bitcoin message components
- `README.md`: Project documentation