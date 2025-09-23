# Workflow ID: limr_82_0
# Benchmark: limr
# Data Indices: [268, 223]

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

        # Phase 1: Problem Analysis and Decomposition
        problem_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (e.g., algebra, geometry, combinatorics).
            - Extract all given variables, constraints, and relationships.
            - Highlight any special conditions or edge cases.
            - Suggest potential solution strategies.
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Solution Exploration
        algebraic_solution, geometric_solution, combinatorial_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using algebraic methods:
                - Perform symbolic manipulations.
                - Solve equations step-by-step.
                - Verify intermediate results.
                Problem context: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using geometric reasoning:
                - Analyze shapes, coordinates, or transformations.
                - Apply relevant theorems or properties.
                - Verify calculations.
                Problem context: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using combinatorial techniques:
                - Count possibilities systematically.
                - Evaluate probabilities or permutations.
                - Verify logic.
                Problem context: {problem_analysis}""",
                context=problem_analysis
            )
        )

        # Phase 3: Intermediate Verification and Refinement
        refined_solutions = await asyncio.gather(
            self.revise(
                instruction="Verify and refine the algebraic solution for correctness.",
                context=algebraic_solution
            ),
            self.revise(
                instruction="Verify and refine the geometric solution for correctness.",
                context=geometric_solution
            ),
            self.revise(
                instruction="Verify and refine the combinatorial solution for correctness.",
                context=combinatorial_solution
            )
        )

        # Phase 4: Ensemble Decision and Finalization
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Mathematical rigor.
            - Alignment with problem requirements.
            - Clarity and simplicity.
            If multiple solutions are valid, synthesize them into a unified answer.""",
            contexts_list=refined_solutions
        )

        # Phase 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="Extract the final integer answer from the solution.",
            context=final_solution
        )

        return final_answer