# Workflow ID: limr_148_0
# Benchmark: limr
# Data Indices: [132, 262]

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

        # --- Initial Analysis ---
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the domain (geometry, algebra, etc.)
            2. Extract key components (variables, constraints, relationships)
            3. Classify the problem type (proof, computation, optimization, etc.)
            4. Highlight any ambiguities or missing information
            Provide a structured breakdown.""",
            context=""
        )

        # --- Parallel Exploration ---
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"Using the analysis: {analysis}\nAttempt a symbolic/algebraic solution.",
                context=analysis
            ),
            self.generate(
                instruction=f"Using the analysis: {analysis}\nAttempt a geometric/visual solution.",
                context=analysis
            ),
            self.generate(
                instruction=f"Using the analysis: {analysis}\nAttempt a combinatorial/probabilistic solution.",
                context=analysis
            )
        )

        # --- Iterative Refinement ---
        refined_approaches = []
        for approach in approaches:
            refined = await self.revise(
                instruction=f"Validate and improve this solution attempt:\n{approach}\nCorrect any errors and add missing details.",
                context=approach
            )
            refined_approaches.append(refined)

        # --- Ensemble Synthesis ---
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined approaches:
            1. Evaluate correctness and completeness
            2. Resolve conflicts between approaches
            3. Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_approaches
        )

        return final_solution