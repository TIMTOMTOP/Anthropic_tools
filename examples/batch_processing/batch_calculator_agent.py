import anthropic
import asyncio
from typing import List, Dict


class BatchCalculatorAgent:
    """
    An agent that processes multiple calculation requests in batch using Claude's API.
    """

    def __init__(self, api_key: str):
        """Initialize the agent with API credentials and tool definition."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.calculator_tool = self._define_calculator_tool()

    @staticmethod
    def _define_calculator_tool() -> dict:
        """Define the calculator tool that Claude will use for calculations."""
        return {
            "name": "calculate",
            "description": "A simple calculator that can perform basic math operations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The math operation to perform"
                    },
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "The numbers to perform the operation on"
                    }
                },
                "required": ["operation", "numbers"]
            }
        }

    def _create_batch_requests(self, questions: List[str]) -> List[Dict]:
        """
        Create a list of batch requests from the input questions.
        
        Args:
            questions: List of calculation questions to process
            
        Returns:
            List of formatted batch requests for Claude's API
        """
        system_prompt = """
        You are a helpful calculator assistant. When users ask you to perform calculations, 
        use the calculate tool directly without explaining what you're going to do first.
        """

        return [
            {
                "custom_id": f"calculation_{i}",
                "params": {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "tools": [self.calculator_tool],
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": question}]
                }
            }
            for i, question in enumerate(questions)
        ]

    def _perform_calculation(self, operation: str, numbers: List[float]) -> float:
        """
        Perform the requested calculation operation on the provided numbers.
        
        Args:
            operation: One of "add", "subtract", "multiply", "divide"
            numbers: List of numbers to perform the operation on
            
        Returns:
            Result of the calculation
        """
        if operation == "add":
            return sum(numbers)
        elif operation == "subtract":
            return numbers[0] - sum(numbers[1:])
        elif operation == "multiply":
            result = 1
            for num in numbers:
                result *= num
            return result
        elif operation == "divide":
            result = numbers[0]
            for num in numbers[1:]:
                result /= num
            return result
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    async def _process_tool_use(self, message) -> str:
        """
        Process a tool use request from Claude and return the final response.
        
        Args:
            message: The message containing the tool use request
            
        Returns:
            Formatted string containing the calculation result and Claude's response
        """
        if not hasattr(message, 'content'):
            return "Error: No content in message"

        for content in message.content:
            if content.type == "tool_use":
                # Log tool use request
                print(f"\nTool Use Request: {content.name}")
                print(f"Input: {content.input}")

                # Execute calculation
                try:
                    result = self._perform_calculation(
                        content.input["operation"],
                        content.input["numbers"]
                    )
                    print(f"Calculation Result: {result}")

                    return f"Result: {result}"
                except Exception as e:
                    return f"Error during calculation: {str(e)}"

        return "No tool use found in message"

    async def _monitor_batch_progress(self, batch_id: str, expected_count: int) -> dict:
        """
        Monitor the progress of a batch request and process results as they arrive.
        
        Args:
            batch_id: The ID of the batch to monitor
            expected_count: The number of results we expect
            
        Returns:
            Dictionary mapping custom_ids to their processed results
        """
        results = {}
        processed_count = 0

        while processed_count < expected_count:
            # Check batch status
            batch_status = self.client.beta.messages.batches.retrieve(batch_id)
            print(f"Current batch status: {batch_status.processing_status}")

            if batch_status.processing_status == "ended":
                # Process completed results
                for result in self.client.beta.messages.batches.results(batch_id):
                    if result.custom_id not in results and result.result.type == "succeeded":
                        final_response = await self._process_tool_use(result.result.message)
                        results[result.custom_id] = final_response
                        processed_count += 1
                        print(f"✓ Processed result for {result.custom_id}")

            if processed_count < expected_count:
                await asyncio.sleep(2)
                print(f"⏳ Waiting for results... ({processed_count}/{expected_count})")

        return results

    async def process_calculations(self, questions: List[str]) -> Dict[str, str]:
        """
        Process a list of calculation questions in batch.
        
        Args:
            questions: List of calculation questions to process
            
        Returns:
            Dictionary mapping question IDs to their results
        """
        print("\n1️⃣ Creating batch calculation requests...")
        batch_requests = self._create_batch_requests(questions)
        batch = self.client.beta.messages.batches.create(requests=batch_requests)

        print(f"\n2️⃣ Processing batch (ID: {batch.id})...")
        results = await self._monitor_batch_progress(batch.id, len(questions))

        print("\n✅ All calculations completed!")
        return results
