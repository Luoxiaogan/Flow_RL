# Workflow ID: mbppplus_42_0
# Benchmark: mbppplus
# Data Indices: [171, 78, 304]

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

        # Step 1: Classify problem type and extract key entities
        classification = await self.generate(
            instruction="""Analyze the programming problem and classify it:
            1. Problem Type: Is it (a) String/List Filtering, (b) Data Structure Access, (c) Mathematical Computation, or (d) Logical/Validation?
            2. Key Entities: Extract function name, parameter names and types, expected return type.
            3. Edge Cases: What edge cases should be handled? (e.g., empty inputs, index out of bounds, zero/negative numbers)
            4. Constraints: Any explicit or implicit constraints from the problem description?
            5. Solution Strategy: Suggest 1-2 high-level approaches to solve this.
            Format your response clearly with these numbered sections.""",
            context=""
        )

        # Step 2: Generate multiple solution candidates in parallel based on classification
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this classification:
                {classification}

                Generate a Python solution focusing on SIMPLICITY and READABILITY.
                - Use straightforward logic, even if less efficient.
                - Include comments for key steps.
                - Handle edge cases mentioned in classification.
                - Match exact function signature and return type shown in examples.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}

                Generate a Python solution focusing on ROBUSTNESS and EDGE CASES.
                - Add defensive checks for invalid inputs.
                - Handle all edge cases explicitly.
                - Use try/except if appropriate.
                - Ensure type consistency with test cases.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}

                Generate a Python solution focusing on PERFORMANCE and EFFICIENCY.
                - Optimize for speed or memory if applicable.
                - Use built-in functions or libraries if allowed.
                - Avoid unnecessary computations.
                - Still handle critical edge cases.""",
                context=classification
            )
        )

        # Step 3: Revise each candidate for correctness and edge case handling
        revised_candidates = []
        for candidate in solution_candidates:
            revised = await self.revise(
                instruction="""Critique and improve this code:
                1. Check for off-by-one errors, type mismatches, boundary conditions.
                2. Ensure return type exactly matches test cases (list vs tuple vs string vs int).
                3. Handle empty inputs, single-element cases, duplicates, negative numbers as appropriate.
                4. Improve variable names and add minimal comments if missing.
                5. Remove any print statements or debug code.
                Return only the improved function implementation.""",
                context=candidate
            )
            revised_candidates.append(revised)

        # Step 4: Ensemble - Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below:
            - Prioritize CORRECTNESS and EDGE CASE HANDLING above all.
            - If multiple are correct, choose the most READABLE and MAINTAINABLE.
            - If they can be combined into a superior solution, synthesize them.
            - Ensure the function signature exactly matches the original (same name, parameters).
            - Return ONLY the Python function code, no explanations or markdown.
            - Include necessary imports inside the function if any (e.g., import math).""",
            contexts_list=revised_candidates
        )

        # Step 5: Final cleanup - extract only the function code
        clean_code = await self.summarize(
            instruction="""Extract ONLY the Python function implementation from the text below.
            - Remove all markdown, explanations, and extra text.
            - Return only the function definition with any necessary imports.
            - Preserve exact function signature and indentation.
            - If no function is found, return the original text unchanged.""",
            context=final_solution
        )

        return clean_code