# Workflow ID: limr_22_0
# Benchmark: limr
# Data Indices: [165, 236]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Classify this problem:
            1. Identify its type (algebraic, geometric, combinatorial, etc.).
            2. Extract key components (variables, constraints, relationships).
            3. Determine the expected answer format.
            Provide structured classification.""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Refine the analysis to ensure completeness and accuracy.",
            context=initial_analysis
        )

        # Step 2: Parallel Exploration
        algebraic_solution = self.generate(
            instruction=f"Attempt an algebraic solution based on: {refined_analysis}",
            context=refined_analysis
        )
        geometric_solution = self.generate(
            instruction=f"Attempt a geometric solution based on: {refined_analysis}",
            context=refined_analysis
        )
        combinatorial_solution = self.generate(
            instruction=f"Attempt a combinatorial solution based on: {refined_analysis}",
            context=refined_analysis
        )
        solutions = await asyncio.gather(algebraic_solution, geometric_solution, combinatorial_solution)

        # Step 3: Validation and Refinement
        validated_solutions = []
        for solution in solutions:
            validation = await self.generate(
                instruction=f"Validate the solution: {solution}. Check for logical consistency and correctness.",
                context=solution
            )
            if "error" in validation.lower():
                revised = await self.revise(
                    instruction=f"Correct the following issues: {validation}",
                    context=solution
                )
                validated_solutions.append(revised)
            else:
                validated_solutions.append(solution)

        # Step 4: Final Synthesis
        final_solution = await self.ensemble(
            instruction="Synthesize the best solution from the validated attempts. Ensure the answer is precise and formatted correctly.",
            contexts_list=validated_solutions
        )

        return final_solution