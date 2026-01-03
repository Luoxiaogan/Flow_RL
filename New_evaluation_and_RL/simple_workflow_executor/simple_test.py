"""
Simple test for Verifier-Refiner workflow
"""

import asyncio
from simple_executor import SimpleWorkflowExecutor

# Simple workflow with Verifier-Refiner loop
SIMPLE_WORKFLOW = '''
import asyncio
import json

class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem_text = problem

        # Import and create operators
        try:
            from metagpt.provider.llm_provider_registry import create_llm_instance as create
            import ScoreFlow.scripts.common.operator as operator

            self.llm = create(config)
            self.generate = operator.Generate(self.llm, self.problem_text)
            self.verifier = operator.Verifier(self.llm, self.problem_text)
            self.refiner = operator.Refiner(self.llm, self.problem_text)
            print("Operators initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize operators: {e}")
            # Create mock operators for testing
            self.generate = lambda **kwargs: "Initial solution to the problem"
            self.verifier = lambda **kwargs: {"verdict": "correct", "findings": []}
            self.refiner = lambda **kwargs: {"refined_solution": "Refined solution"}

    async def run_workflow(self):
        print("Starting Verifier-Refiner workflow...")

        # Step 1: Generate initial solution
        print("Step 1: Generating initial solution...")
        solution = await self.generate(
            instruction="Solve this problem step by step",
            context=""
        )

        # Step 2: Verify solution
        print("Step 2: Verifying solution...")
        verification = await self.verifier(
            instruction="Verify this solution",
            context=solution
        )

        # Step 3: Refine if needed
        verdict = str(verification.get("verdict", "")).lower()
        if "invalid" in verdict or "incorrect" in verdict:
            print("Step 3: Refining solution...")
            refined = await self.refiner(
                instruction="Fix the issues",
                context=solution,
                verification_feedback=json.dumps(verification)
            )
            solution = refined.get("refined_solution", solution)
        else:
            print("Step 3: Solution passed verification")

        return f"Final Answer: {solution}"

    async def __call__(self):
        try:
            return await asyncio.wait_for(self.run_workflow(), timeout=180)
        except Exception as e:
            return f"Error: {str(e)}"
'''

async def main():
    print("=" * 60)
    print("Testing Verifier-Refiner Workflow")
    print("=" * 60)

    # Create executor
    executor = SimpleWorkflowExecutor()

    # Test problem
    problem = "Prove that for any positive integer n, the sum 1 + 2 + ... + n equals n(n+1)/2."

    print(f"Problem: {problem}")
    print("=" * 60)

    # Execute workflow
    result = await executor.execute_workflow(
        workflow_code=SIMPLE_WORKFLOW,
        problem_text=problem,
        benchmark_name="test",
        test_case=1
    )

    # Show results
    print("=" * 60)
    print("Execution Result:")
    print("=" * 60)

    if result['success']:
        print(f"Status: SUCCESS")
        print(f"Time: {result.get('execution_time', 0):.2f}s")
        print(f"Output: {result.get('result', 'No output')}")
    else:
        print(f"Status: FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())