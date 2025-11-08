# NationStates AI Governance Simulator

This project is an AI-powered simulator for NationStates, a nation simulation game. It uses a local LLM (via Ollama) to make governance decisions on issues that arise in your nation.

## Features

- Automatically fetches and responds to NationStates issues
- Uses AI (Llama 3.2 3B model) to choose the best policy options
- Logs all decisions to an NDJSON file for analysis
- Supports test mode for safe experimentation
- Rate-limited to respect NationStates API guidelines

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running locally
- Llama 3.2 3B model: `ollama pull llama3.2:3b`
- A NationStates account with API access

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/kunpai/LLMs-Play-NationStates.git
   cd LLMs-Play-NationStates
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. Create a `.env` file in the project root with your NationStates credentials:
   ```
   NATION=your_nation_name
   PASSWORD=your_password
   USER_AGENT=Your App Name/1.0 (contact@example.com)
   SLEEP_BETWEEN_REQUESTS=10
   TEST_MODE=false
   ```

2. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

## Usage

Run the simulator:
```bash
python main.py
```

In test mode (set `TEST_MODE=true` in `.env`), it will log decisions without submitting them.

The script checks for new issues every hour. Decisions are logged to `choices.ndjson`.

## Configuration

- `NATION`: Your NationStates nation name
- `PASSWORD`: Your NationStates password
- `USER_AGENT`: A descriptive user agent for API requests
- `SLEEP_BETWEEN_REQUESTS`: Seconds to wait between API calls (default: 10)
- `TEST_MODE`: Set to `true` to test without submitting answers

## Logging

All decisions are logged to `choices.ndjson` in NDJSON format, including:
- Timestamp
- Issue ID and text
- Chosen option
- Selection method (AI or random fallback)

## Disclaimer

This tool interacts with NationStates' API. Use responsibly and in accordance with their terms of service. The AI makes decisions based on the prompt, which prioritizes economic stability, civil rights, and political freedom.

## License

MIT License