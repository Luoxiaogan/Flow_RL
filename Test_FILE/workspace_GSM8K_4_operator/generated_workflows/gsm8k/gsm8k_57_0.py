# Workflow ID: gsm8k_57_0
# Benchmark: gsm8k
# Data Indices: [246, 16]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Initial Analysis: Extract key information and structure the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values and their context from the problem. 
            Identify what the question asks for and outline potential solution steps.""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Develop a solution using arithmetic operations: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a solution using proportions and fractions: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Develop a solution using rate-based calculations: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Synthesize the best approach
        best_path = await self.ensemble(
            instruction="Choose the most promising solution path based on clarity, completeness, and correctness.",
            contexts_list=solution_paths
        )

        # Step-by-Step Calculation: Build and refine the solution chain
        refined_solution = await self.revise(
            instruction="Refine the solution by verifying each step, correcting errors, and ensuring precision.",
            context=best_path
        )

        # Final Validation: Ensure accuracy and present the final answer
        final_answer = await self.summarize(
            instruction="Condense the refined solution into a final numerical answer, showing all key steps.",
            context=refined_solution
        )

        return final_answer