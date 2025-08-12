# Workflow ID: high_level_math_ganluo_26_0
# Benchmark: high_level_math_ganluo
# Data Indices: [22]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        """
        import asyncio

        # Step 1: Extract problem parameters
        extraction = await self.generate(
            instruction="Extract the coin denominations and the range of N from the problem text. "
                        "Return the denominations as a list of integers and the range as a tuple (start, end).",
            context=self.problem_text
        )
        denominations, (start, end) = eval(extraction)  # Parse the extracted parameters

        # Step 2: Define the greedy algorithm
        greedy_logic = await self.generate(
            instruction=f"Write a Python function `greedy_algorithm(N)` that computes the number of coins "
                        f"required for a given value N using the greedy approach with denominations {denominations}. "
                        "The function should return the total number of coins used.",
            context=self.problem_text
        )

        # Step 3: Define the optimal solution logic
        optimal_logic = await self.generate(
            instruction=f"Write a Python function `optimal_solution(N)` that computes the minimum number of coins "
                        f"required for a given value N using all possible combinations of denominations {denominations}. "
                        "The function should return the total number of coins used.",
            context=self.problem_text
        )

        # Step 4: Refine logic for edge cases
        refined_greedy = await self.revise(
            instruction="Ensure the greedy algorithm handles edge cases like N = 1 and N = 1000 correctly.",
            context=greedy_logic
        )
        refined_optimal = await self.revise(
            instruction="Ensure the optimal solution logic handles edge cases like N = 1 and N = 1000 correctly.",
            context=optimal_logic
        )

        # Step 5: Evaluate for all N in parallel
        async def evaluate_n(n):
            greedy_result = eval(refined_greedy)(n)
            optimal_result = eval(refined_optimal)(n)
            return n, greedy_result == optimal_result

        tasks = [evaluate_n(n) for n in range(start, end + 1)]
        results = await asyncio.gather(*tasks)

        # Step 6: Count successful N values
        success_count = sum(1 for _, success in results if success)

        # Step 7: Summarize the final result
        summary = await self.summarize(
            instruction="Summarize the total count of successful N values where the greedy algorithm matches the optimal solution.",
            context=str(success_count)
        )

        return summary