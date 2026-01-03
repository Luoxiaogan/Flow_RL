# Workflow ID: mbpp_26_0
# Benchmark: mbpp
# Data Indices: [152, 145]

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

        # Step 1: Extract function name, parameters, and requirements
        analysis = await self.generate(
            instruction="""Extract the function name, parameters, and expected behavior:
            - Analyze the assert statements to identify the function name and its arguments.
            - Parse the task description to infer the complete requirements.
            - Identify edge cases and constraints from the test cases.""",
            context=""
        )

        # Step 2: Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on mathematical computation:
                - Use standard library functions where applicable.
                - Ensure the function matches the extracted name and parameters: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on algorithmic logic:
                - Use list comprehensions, sorting, or other algorithmic constructs.
                - Ensure the function matches the extracted name and parameters: {analysis}""",
                context=analysis
            )
        )

        # Step 3: Validate and refine candidates
        refined_candidates = []
        for candidate in candidates:
            validation = await self.generate(
                instruction=f"""Validate this solution against the test cases:
                - Check if the function passes all assert statements.
                - Identify any errors or missing details.
                Solution: {candidate}""",
                context=analysis
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Fix issues in the solution:
                    - Address errors identified in the validation: {validation}
                    - Improve clarity and ensure proper formatting.""",
                    context=candidate
                )
                refined_candidates.append(refined)
            else:
                refined_candidates.append(candidate)

        # Step 4: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Prioritize correctness, clarity, and adherence to formatting rules.
            - Consider edge cases and completeness.""",
            contexts_list=refined_candidates
        )

        return final_solution