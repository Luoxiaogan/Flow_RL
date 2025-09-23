# Workflow ID: mbppplus_31_0
# Benchmark: mbppplus
# Data Indices: [365, 329]

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
        import json

        # Step 1: Classify the problem type and extract key requirements
        classification = await self.generate(
            instruction="""Analyze this programming problem and classify it along these dimensions:
            1. Primary domain: Is it string manipulation, list/tuple operations, mathematical computation, data structure algorithm, or logic/validation?
            2. Key operations needed: Filtering, transforming, searching, sorting, pattern matching, etc.
            3. Critical edge cases: What boundary conditions must be handled? (e.g., empty inputs, single elements, duplicates, type variations)
            4. Return type requirements: Must the solution return a specific type (list, tuple, set, string, etc.)?
            5. Special constraints: Any performance, library, or style constraints?
            Format your response as a structured JSON with keys: domain, operations, edge_cases, return_type, constraints.""",
            context=""
        )

        # Step 2: Decompose complex problems into subtasks
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, independent subproblems that can be solved separately.
            Each subproblem should be atomic and testable. Consider:
            - Input preprocessing steps
            - Core algorithmic steps
            - Output postprocessing steps
            - Edge case handling as separate subproblems if complex
            Return a list of subproblems with dependencies between them.""",
            context=classification
        )

        # Step 3: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a Python solution using a {strategy} approach.
                Problem classification: {classification}
                Subproblems to solve: {[sub['description'] for sub in decomposition]}
                Requirements:
                - Handle all edge cases mentioned in classification
                - Match exact return type specified
                - Use clean, readable code with meaningful variable names
                - Include necessary imports
                - Return ONLY the function implementation (no explanations)
                Strategy: {strategy}""",
                context=""
            ) for strategy in [
                "direct implementation with built-in functions",
                "step-by-step algorithmic approach",
                "functional programming with comprehensions and filters"
            ]
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # Step 4: Validate each solution against inferred test cases
        validation_tasks = []
        for i, solution in enumerate(strategy_solutions):
            validation = await self.generate(
                instruction=f"""Generate 5 test cases (including edge cases) for this problem based on the classification.
                Then, analyze whether the following solution handles all cases correctly:
                Solution: {solution}
                Classification: {classification}
                Return a JSON with keys: test_cases (list of input-output pairs), issues (list of problems found), confidence_score (1-10).""",
                context=solution
            )
            validation_tasks.append(validation)
        
        validations = await asyncio.gather(*validation_tasks)

        # Step 5: Ensemble - select best solution or synthesize
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Highest confidence score from validation
            2. Fewest issues identified
            3. Cleanest, most readable code
            4. Best handling of edge cases
            If multiple solutions are strong, synthesize a hybrid solution combining their strengths.
            Return ONLY the final function implementation (no explanations).""",
            contexts_list=strategy_solutions
        )

        # Step 6: Revise for type safety and edge cases
        final_solution = await self.revise(
            instruction=f"""Review this solution for:
            1. Type consistency: Does it return exactly the type specified in classification ({classification})?
            2. Edge case handling: Does it explicitly handle all edge cases from classification?
            3. Error prevention: Does it gracefully handle unexpected inputs?
            4. Code cleanliness: Are variable names meaningful? Is logic clear?
            Make necessary revisions. Return ONLY the function implementation.""",
            context=best_solution
        )

        # Step 7: Final validation with programmer execution (if code is parseable)
        try:
            # Extract function name for testing
            func_name = re.search(r"def\s+(\w+)", final_solution)
            if func_name:
                func_name = func_name.group(1)
                test_context = f"""Function name: {func_name}
                Classification: {classification}
                Attempt to execute this code with sample inputs from classification.
                Return any execution errors or validation failures."""
                
                executed = await self.programmer(
                    instruction=test_context,
                    context=final_solution,
                    max_retries=2
                )
                
                # If execution reveals issues, do one final revision
                if "error" in executed.lower() or "exception" in executed.lower():
                    final_solution = await self.revise(
                        instruction=f"""The following code failed execution or validation:
                        Execution result: {executed}
                        Revise the code to fix these issues while maintaining all requirements.
                        Return ONLY the corrected function implementation.""",
                        context=final_solution
                    )
        except Exception:
            # If anything fails in execution phase, stick with revised solution
            pass

        return final_solution