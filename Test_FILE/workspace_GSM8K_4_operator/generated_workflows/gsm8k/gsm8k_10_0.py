# Workflow ID: gsm8k_10_0
# Benchmark: gsm8k
# Data Indices: [144, 60]

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
            instruction="""Extract all numerical values, their context, and the question being asked.
            Classify the problem type (e.g., percentage change, rate problem, distribution).
            Provide structured information including:
            - Known quantities and their units
            - Relationships between quantities
            - What needs to be solved""",
            context=""
        )

        # Step 2: Solution Generation (Parallel Fork)
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information: {initial_analysis}
                Solve the problem using direct calculation methods.
                Show all intermediate steps and maintain precision.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information: {initial_analysis}
                Solve the problem using proportional reasoning.
                Show all intermediate steps and maintain precision.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement (Iterative Loop)
        refined_solutions = []
        for solution in solutions:
            refined = await self.revise(
                instruction="Validate and refine the solution. Check for arithmetic errors, logical consistency, and unit correctness.",
                context=solution
            )
            refined_solutions.append(refined)

        # Step 4: Final Synthesis (Ensemble)
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution. Ensure it answers the original question.",
            contexts_list=refined_solutions
        )

        # Step 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution. Discard intermediate details.",
            context=final_solution
        )

        return final_answer