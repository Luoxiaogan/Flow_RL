# Workflow ID: high_level_math_ganluo_22_0
# Benchmark: high_level_math_ganluo
# Data Indices: [14]

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

        # Step 1: Extract key constraints and mathematical structure
        extraction = await self.generate(
            instruction="Extract all numerical values, variables, and constraints from the problem. "
                        "Identify the type of mathematical structure (e.g., modular arithmetic, combinatorics). "
                        "Provide a detailed breakdown of what needs to be solved.",
            context=self.problem_text
        )

        # Step 2: Generate multiple solution approaches
        approach1 = self.generate(
            instruction=f"Using the extracted information: {extraction}, "
                        "solve the problem using direct computation. "
                        "Provide step-by-step reasoning and intermediate results.",
            context=self.problem_text
        )
        approach2 = self.generate(
            instruction=f"Using the extracted information: {extraction}, "
                        "solve the problem using casework analysis. "
                        "Consider all possible cases and compute their contributions.",
            context=self.problem_text
        )
        approach3 = self.generate(
            instruction=f"Using the extracted information: {extraction}, "
                        "solve the problem by exploiting symmetry or simplifying assumptions. "
                        "Provide justification for any shortcuts or optimizations.",
            context=self.problem_text
        )

        # Execute approaches in parallel
        results = await asyncio.gather(approach1, approach2, approach3)

        # Step 3: Validate and refine solutions
        refined_results = await asyncio.gather(
            self.revise(
                instruction="Critique and refine this solution. Ensure all constraints are satisfied and calculations are correct.",
                context=results[0]
            ),
            self.revise(
                instruction="Critique and refine this solution. Ensure all constraints are satisfied and calculations are correct.",
                context=results[1]
            ),
            self.revise(
                instruction="Critique and refine this solution. Ensure all constraints are satisfied and calculations are correct.",
                context=results[2]
            )
        )

        # Step 4: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="Compare the refined solutions and select the most accurate and complete one. "
                        "If multiple solutions are valid, synthesize them into a single coherent answer.",
            contexts=refined_results
        )

        # Step 5: Summarize the final result
        summary = await self.summarize(
            instruction="Condense the final solution into a clear and concise format. "
                        "Ensure the answer satisfies all problem constraints and is presented as required (e.g., remainder when divided by 1000).",
            context=final_solution
        )

        return summary