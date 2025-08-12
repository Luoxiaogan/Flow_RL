# Workflow ID: high_level_math_ganluo_27_0
# Benchmark: high_level_math_ganluo
# Data Indices: [2]

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

        # Step 1: Extract problem parameters and constraints
        extraction = await self.generate(
            instruction="Extract all numerical values, constraints, and conditions from the problem. "
                        "Identify the total number of entities (e.g., players), categories (e.g., flavors), "
                        "and any hierarchical or inequality constraints.",
            context=self.problem_text
        )

        # Step 2: Generate candidate solutions
        candidates = await self.generate(
            instruction=f"Based on the extracted information: {extraction}, generate all possible assignments "
                        "of entities to categories that satisfy basic conditions (e.g., at least one entity per category). "
                        "Provide these assignments in a structured format.",
            context=self.problem_text
        )

        # Step 3: Revise solutions to enforce constraints
        revised_solutions = await self.revise(
            instruction=f"Filter the candidate solutions to ensure they meet all constraints, including hierarchical "
                        f"ordering and inequality conditions. Specifically, ensure that the number of entities in each "
                        f"category adheres to the relationships described in the problem.",
            context=candidates
        )

        # Step 4: Aggregate and verify results
        final_count = await self.ensemble(
            instruction="Count the number of valid assignments from the revised solutions. "
                        "Ensure that all constraints are satisfied and no duplicates exist.",
            contexts=[revised_solutions]
        )

        # Step 5: Compute the final result (e.g., modulo operation)
        final_result = await self.generate(
            instruction=f"Compute the remainder when the total count ({final_count}) is divided by 1000. "
                        "Provide the final numerical result.",
            context=self.problem_text
        )

        return final_result