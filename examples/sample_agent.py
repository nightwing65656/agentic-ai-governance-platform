"""
Sample Agent Fixture for Testing

This is a minimal, permitted sample agent for testing instrumentation and security scanning.
It simulates a simple research agent that calls a tool and returns a result.

NOTE: This is for demonstration purposes only. Do not use in production.
"""

from typing import Any

from src.instrumentation.agent_trace import operational_trace


# Simulated tool: fetch_market_data
def fetch_market_data(symbol: str) -> dict[str, Any]:
    """Simulate fetching market data for a given symbol."""
    return {
        "symbol": symbol,
        "price": 150.25,
        "change": 2.5,
        "volume": 1_000_000,
    }


# Simulated agent: ResearchAgent
class ResearchAgent:
    """A simple research agent that fetches market data and returns a summary."""

    def __init__(self, name: str = "ResearchAgent") -> None:
        self.name = name

    @operational_trace()
    def run(self, symbol: str) -> str:
        """Run the agent for a given stock symbol."""
        # Call tool
        data = fetch_market_data(symbol)

        # Generate summary (deterministic, no LLM for simplicity)
        return (
            f"Symbol: {data['symbol']}\n"
            f"Price: ${data['price']}\n"
            f"Change: {data['change']}%\n"
            f"Volume: {data['volume']:,}"
        )


# Entry point for demo
if __name__ == "__main__":
    agent = ResearchAgent()
    print(agent.run("AAPL"))