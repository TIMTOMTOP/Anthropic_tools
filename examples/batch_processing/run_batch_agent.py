import os
import asyncio
import dotenv
from batch_calculator_agent import BatchCalculatorAgent

dotenv.load_dotenv()

async def main():
    """Example usage of the BatchCalculatorAgent."""
    agent = BatchCalculatorAgent(os.getenv("ANTHROPIC_API_KEY"))

    questions = [
        "What is 25 + 17?",
        "What is 100 ÷ 4?",
        "What is 13 × 7?"
    ]

    results = await agent.process_calculations(questions)
    
    print("\nResults:")
    for question_id, response in results.items():
        print(f"\n{question_id}:")
        print(response)

if __name__ == "__main__":
    asyncio.run(main())