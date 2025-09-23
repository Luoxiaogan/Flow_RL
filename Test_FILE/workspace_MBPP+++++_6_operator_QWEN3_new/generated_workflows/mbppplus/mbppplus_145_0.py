# Workflow ID: mbppplus_145_0
# Benchmark: mbppplus
# Data Indices: [294, 48]

import asyncio

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Analyze the programming problem and classify it by:
            1. Primary category: [List/Tuple Operations, String Manipulation, Mathematical Computation, Data Structure Algorithm, Logic Problem]
            2. Algorithmic paradigm: [Iterative, Recursive, Dynamic Programming, Greedy, Divide-and-Conquer, Brute Force, etc.]
            3. Key edge cases to handle: [Empty inputs, single elements, duplicates, negative numbers, type mismatches, etc.]
            4. Expected input/output types and structure.
            5. Any implicit constraints or assumptions.
            Format your response as a structured JSON-like summary.""",
            context=""
        )

        # Step 2: Decompose into subproblems
        subproblems = await self.decompose(
            instruction="""Break down the problem into atomic, sequentially dependent subproblems.
            Each subproblem should be solvable independently once its dependencies are met.
            Focus on: input validation, edge case handling, core logic implementation, and output formatting.
            Return as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=classification
        )

        # Step 3: Generate multiple solution hypotheses in parallel
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python solution using an ITERATIVE approach.
                Consider edge cases identified in classification: {classification}
                Ensure type consistency and handle all boundary conditions.
                Return ONLY the function implementation as specified in the problem.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python solution using a RECURSIVE or DYNAMIC PROGRAMMING approach.
                Consider edge cases identified in classification: {classification}
                Optimize for clarity and correctness, not performance.
                Return ONLY the function implementation as specified in the problem.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python solution using a FUNCTIONAL or SET-BASED approach.
                Consider edge cases identified in classification: {classification}
                Use built-in functions and comprehensions where appropriate.
                Return ONLY the function implementation as specified in the problem.""",
                context=""
            )
        )

        # Step 4: Validate each hypothesis against synthetic edge cases
        validation_tasks = []
        for i, hypothesis in enumerate(solution_hypotheses):
            validation = self.programmer(
                instruction=f"""Execute this code against the following test cases:
                - Empty input
                - Single element
                - All negative numbers
                - Mixed types (if applicable)
                - Maximum/minimum boundary values
                Return 'PASS' if all tests pass, 'FAIL' with error details otherwise.
                Code to test:
                {hypothesis}""",
                context=classification
            )
            validation_tasks.append(validation)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # Step 5: Ensemble best solution or trigger revision
        passed_solutions = [
            sol for sol, val in zip(solution_hypotheses, validation_results) 
            if "PASS" in val.upper()
        ]

        if passed_solutions:
            if len(passed_solutions) == 1:
                final_solution = passed_solutions[0]
            else:
                final_solution = await self.ensemble(
                    instruction="""Select the most robust, readable, and efficient solution.
                    Prioritize: correctness > readability > performance.
                    Ensure it handles all edge cases and matches expected output format.""",
                    contexts_list=passed_solutions
                )
        else:
            # All solutions failed - revise with error feedback
            error_summary = "\n".join(validation_results)
            revised_solution = await self.revise(
                instruction=f"""Revise the solution to fix these errors:
                {error_summary}
                
                Incorporate explicit edge case handling for:
                - Empty inputs
                - Single elements
                - Type consistency
                - Boundary conditions
                
                Return ONLY the corrected function implementation.""",
                context=solution_hypotheses[0]  # Start with first hypothesis
            )
            final_solution = revised_solution

        # Step 6: Final validation and cleanup
        final_validation = await self.programmer(
            instruction="""Perform final validation with comprehensive edge cases.
            If any issues remain, return the corrected code.
            Otherwise, return the original code unchanged.
            Ensure output matches exact format specified in problem.""",
            context=final_solution
        )

        # Extract just the code block if validation returns more than code
        code_match = re.search(r'