# Workflow ID: mbpp_52_0
# Benchmark: mbpp
# Data Indices: [294, 71]

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

        # Step 1: Extract function name
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the test cases. 
            Look for the pattern 'assert <function_name>(...)'. 
            Return only the function name.""",
            context=""
        )

        # Step 2: Parse task description
        task_analysis = await self.generate(
            instruction=f"""Analyze the task description to understand the problem's requirements. 
            Focus on key phrases and infer the expected input/output types. 
            Cross-reference with the function name: {function_name_extraction}. 
            Provide a structured summary of the task.""",
            context=""
        )

        # Step 3: Identify edge cases
        edge_cases = await self.generate(
            instruction=f"""Identify potential edge cases based on the task description: {task_analysis}. 
            Consider inputs like empty lists, single-element lists, negative numbers, etc. 
            Return a list of edge cases.""",
            context=task_analysis
        )

        # Step 4: Generate candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on efficiency. 
                Use the task analysis: {task_analysis} and edge cases: {edge_cases}. 
                Ensure the function name is {function_name_extraction}.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on readability. 
                Use the task analysis: {task_analysis} and edge cases: {edge_cases}. 
                Ensure the function name is {function_name_extraction}.""",
                context=""
            )
        )

        # Step 5: Validate and refine
        refined_candidates = []
        for candidate in candidates:
            validation = await self.generate(
                instruction=f"""Validate this solution against the test cases. 
                If errors are found, suggest corrections. 
                Solution: {candidate}""",
                context=""
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Revise the solution to fix errors: {validation}. 
                    Original solution: {candidate}""",
                    context=candidate
                )
                refined_candidates.append(refined)
            else:
                refined_candidates.append(candidate)

        # Step 6: Ensemble selection
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Passing all test cases
            - Clarity of implementation
            - Adherence to Python best practices""",
            contexts_list=refined_candidates
        )

        return final_solution