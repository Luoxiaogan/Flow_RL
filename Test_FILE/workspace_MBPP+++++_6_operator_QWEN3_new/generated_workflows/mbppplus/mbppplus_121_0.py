# Workflow ID: mbppplus_121_0
# Benchmark: mbppplus
# Data Indices: [363, 157]

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
        import json
        import re

        # Step 1: Classify problem complexity and generate edge cases
        classification = await self.generate(
            instruction="""Analyze this programming problem and classify it:
            1. Complexity level: trivial (single operation), moderate (2-3 steps), complex (nested logic, multiple data structures)
            2. Primary category: string manipulation, list/tuple processing, mathematical computation, dictionary/aggregation, or logic/validation
            3. Critical edge cases: generate at least 5 test cases including empty inputs, single elements, duplicates, type boundaries, and malformed inputs
            4. Expected return type: infer from problem context (list, tuple, dict, bool, int, etc.)
            Format as JSON with keys: complexity, category, edge_cases (list of dicts with 'input' and 'expected'), return_type""",
            context=""
        )

        # Step 2: Conditional decomposition based on complexity
        subproblems = []
        try:
            class_data = json.loads(classification)
            if class_data.get("complexity", "moderate") in ["moderate", "complex"]:
                subproblems = await self.decompose(
                    instruction=f"""Break this {class_data.get('category', 'general')} problem into atomic subproblems:
                    - Each subproblem must be independently solvable
                    - Include data transformation steps (e.g., 'convert lists to tuples for hashing')
                    - Specify validation checks for each step
                    - Order by dependency (prerequisites first)
                    Focus on the core challenge: {class_data.get('category', 'unknown')}""",
                    context=classification
                )
        except:
            # Fallback: treat as moderate complexity
            subproblems = []

        # Step 3: Parallel solution generation
        solution_approaches = [
            "imperative: use explicit loops and conditionals with detailed error handling",
            "functional: use comprehensions, map/filter, and built-in functions",
            "library-assisted: leverage collections, itertools, or other stdlib modules where appropriate"
        ]
        
        solution_tasks = []
        for approach in solution_approaches:
            task = self.generate(
                instruction=f"""Generate a complete Python function solution using {approach} style:
                Problem context: {self.problem_text}
                Classification: {classification}
                Subproblems (if any): {json.dumps(subproblems) if subproblems else 'None'}
                Requirements:
                - Handle all edge cases from classification
                - Match exact return type specified
                - Include type annotations if appropriate
                - No external imports unless absolutely necessary
                - Return only the function implementation (no test code)
                Format: pure Python code block starting with 'def'""",
                context=""
            )
            solution_tasks.append(task)
        
        raw_solutions = await asyncio.gather(*solution_tasks)

        # Step 4: Validate solutions against edge cases
        validation_tasks = []
        for i, solution in enumerate(raw_solutions):
            validation_task = self.programmer(
                instruction=f"""Execute this solution against the edge cases from classification.
                For each test case, verify:
                1. Correct output value
                2. Exact return type match
                3. No exceptions on edge inputs
                4. Performance on large inputs (if applicable)
                Return JSON with keys: passed (bool), failed_cases (list), error_messages (list), solution_index ({i})
                Edge cases: {json.dumps(class_data.get('edge_cases', [])) if 'class_data' in locals() else '[]'}""",
                context=solution,
                max_retries=2
            )
            validation_tasks.append(validation_task)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # Step 5: Ensemble best solution
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on:
            1. Highest number of passed edge cases
            2. Cleanest code structure
            3. Most explicit error handling
            4. Closest match to expected return type
            5. Efficiency and readability
            If no solution passes all tests, combine the strongest elements from multiple solutions.
            Return only the final Python function implementation (no explanations).""",
            contexts_list=raw_solutions
        )

        # Step 6: Final revision for robustness
        final_code = await self.revise(
            instruction=f"""Harden this code for production use:
            - Add explicit type checks for critical inputs
            - Handle all edge cases from classification: {json.dumps(class_data.get('edge_cases', [])) if 'class_data' in locals() else '[]'}
            - Ensure return type exactly matches: {class_data.get('return_type', 'unspecified') if 'class_data' in locals() else 'unspecified'}
            - Remove any debug prints or unnecessary comments
            - Optimize for both correctness and readability
            Return only the final Python function implementation.""",
            context=best_solution
        )

        return final_code