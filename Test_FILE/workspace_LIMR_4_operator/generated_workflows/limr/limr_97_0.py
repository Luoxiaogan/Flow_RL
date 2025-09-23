# Workflow ID: limr_97_0
# Benchmark: limr
# Data Indices: [88, 202]

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

        # Initial Analysis: Classify problem and extract key components
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the problem type (e.g., geometry, number theory, algebra).
            2. Identify key constraints and relationships.
            3. Determine what is being asked (exact value, proof, etc.).
            Provide a structured summary.""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution attempts
        strategies = [
            "Solve using algebraic manipulation and equations.",
            "Solve using combinatorial reasoning and counting principles.",
            "Solve using geometric properties and coordinate systems.",
            "Solve using number-theoretic techniques like modular arithmetic."
        ]
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"Attempt solution using the following strategy: {strategy}",
                context=analysis
            ) for strategy in strategies]
        )

        # Validation and Refinement: Critique and refine each attempt
        refined_solutions = []
        for attempt in solution_attempts:
            refined = await self.revise(
                instruction="Critique and refine the solution attempt. Ensure all steps are rigorous and correct.",
                context=attempt
            )
            refined_solutions.append(refined)

        # Synthesis: Evaluate and select the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate all refined solutions:
            1. Check correctness and precision.
            2. Select the most elegant and robust solution.
            3. Ensure the final answer is an integer between 000 and 999.""",
            contexts_list=refined_solutions
        )

        return final_solution