# Workflow ID: mbpp_63_0
# Benchmark: mbpp
# Data Indices: [127]

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

        # Step 1: Extract function name and analyze task description
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the test cases. 
            Look for patterns like 'assert function_name(...)' and return the substring between 'assert' and the first parenthesis.""",
            context=""
        )
        function_name = re.search(r'assert\s+(\w+)\(', function_name_extraction).group(1)

        task_analysis = await self.generate(
            instruction=f"""Analyze the task description to identify:
            - Key requirements
            - Problem type (e.g., list operations, mathematical computations)
            - Potential edge cases""",
            context=""
        )

        # Step 2: Classify problem type
        problem_type = await self.generate(
            instruction=f"""Classify the problem based on the task analysis:
            {task_analysis}
            
            Common types include:
            - List/Array Operations
            - Mathematical Computations
            - String Manipulation
            - Standard Library Usage
            
            Provide a clear classification.""",
            context=task_analysis
        )

        # Step 3: Generate initial solution attempts
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using list comprehensions or built-in functions for:
                {problem_type}""",
                context=task_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using explicit loops for:
                {problem_type}""",
                context=task_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution leveraging Python's standard library for:
                {problem_type}""",
                context=task_analysis
            )
        )

        # Step 4: Validate and revise solutions
        validated_candidates = []
        for candidate in candidates:
            validation = await self.generate(
                instruction=f"""Validate this solution against the test cases:
                {candidate}""",
                context=self.problem_text
            )
            if "error" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Revise the solution to fix:
                    {validation}""",
                    context=candidate
                )
                validated_candidates.append(revised)
            else:
                validated_candidates.append(candidate)

        # Step 5: Ensemble the best solution
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness
            - Simplicity
            - Efficiency""",
            contexts_list=validated_candidates
        )

        # Step 6: Finalize and output code
        final_code = f"""