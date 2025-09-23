# Workflow ID: mbpp_14_0
# Benchmark: mbpp
# Data Indices: [215, 307]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract key information from the problem:
            - Function name from test cases
            - Input types and expected output
            - Problem category (e.g., list operations, math computations)
            - Any constraints or special conditions
            Provide structured output.""",
            context=""
        )

        # Phase 2: Parallel Solution Exploration
        direct_translation, test_driven, library_utilization = await asyncio.gather(
            self.generate(
                instruction=f"""Translate the problem description directly into Python code:
                {analysis}
                Ensure the function name matches the test cases.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Focus on satisfying the test cases first:
                {analysis}
                Write minimal code that passes all assertions.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Leverage Python's standard library to solve the problem:
                {analysis}
                Identify relevant modules and functions.""",
                context=analysis
            )
        )

        # Phase 3: Validation and Refinement
        async def validate_and_refine(solution, label):
            validation = await self.generate(
                instruction=f"""Validate the following solution against the test cases:
                {solution}
                Report any errors or mismatches.""",
                context=solution
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Fix issues identified in validation:
                    {validation}
                    Improve clarity and correctness.""",
                    context=solution
                )
                return refined
            return solution

        refined_solutions = await asyncio.gather(
            validate_and_refine(direct_translation, "direct_translation"),
            validate_and_refine(test_driven, "test_driven"),
            validate_and_refine(library_utilization, "library_utilization")
        )

        # Phase 4: Final Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best aspects of the refined solutions:
            - Choose the most elegant and efficient implementation
            - Ensure correctness and readability
            - Include all necessary imports""",
            contexts_list=refined_solutions
        )

        return final_solution