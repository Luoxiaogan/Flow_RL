# Workflow ID: mbpp_43_0
# Benchmark: mbpp
# Data Indices: [359, 165]

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
        import re

        # Step 1: Initial Analysis - Extract function name and key components
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the test cases and identify:
            - Input types and formats
            - Output types and formats
            - Key requirements from the task description""",
            context=""
        )

        # Parse function name using regex
        function_name_match = re.search(r"assert (\w+)\(", initial_analysis)
        function_name = function_name_match.group(1) if function_name_match else "solution"

        # Step 2: Problem Classification - Determine problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the task description:
            - Is it a list/array operation, mathematical computation, string manipulation, or standard library usage?
            - What specific patterns or operations are involved?""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Generation
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution for the problem classified as: {classification}.
                Ensure the function name is '{function_name}' and include necessary imports.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate an alternative solution using a different approach for: {classification}.
                Ensure the function name is '{function_name}' and include necessary imports.""",
                context=initial_analysis
            )
        )

        # Step 4: Validation and Refinement
        validated_candidates = []
        for candidate in candidates:
            validation = await self.generate(
                instruction=f"""Validate the following code against the test cases:
                {candidate}
                Identify any failing test cases and explain why.""",
                context=initial_analysis
            )
            if "fail" not in validation.lower():
                validated_candidates.append(candidate)
            else:
                refined = await self.revise(
                    instruction=f"""Refine the following code to fix issues identified in validation:
                    {validation}""",
                    context=candidate
                )
                validated_candidates.append(refined)

        # Step 5: Final Synthesis
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best-performing candidates into a single, optimized solution.
            Ensure the function name is '{function_name}' and include necessary imports.""",
            contexts_list=validated_candidates
        )

        return final_solution