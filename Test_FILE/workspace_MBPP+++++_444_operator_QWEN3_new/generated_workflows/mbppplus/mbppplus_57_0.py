# Workflow ID: mbppplus_57_0
# Benchmark: mbppplus
# Data Indices: [131, 96, 33]

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

        # Step 1: Problem Analysis & Classification
        analysis = await self.generate(
            instruction="""Perform deep problem analysis. Identify:
            1. Primary operation type (string, numeric, logical, data structure)
            2. Input/output data types and structures
            3. Key transformation rules or mathematical relationships
            4. Likely edge cases (empty inputs, single elements, boundaries)
            5. Required return type (list, tuple, int, string, etc.)
            6. Any implicit constraints or assumptions
            Format as structured bullet points with clear categorization.""",
            context=""
        )

        # Step 2: Extract solution blueprint via summarization
        blueprint = await self.summarize(
            instruction="""Condense the analysis into a concise solution blueprint containing:
            - Problem type classification
            - Required input/output handling
            - Critical edge cases to address
            - Return type specification
            - Core algorithmic approach (e.g., iteration, regex, filtering, summation)
            Keep it under 150 words but preserve all essential constraints.""",
            context=analysis
        )

        # Step 3: Parallel solution generation - 3 different approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct, imperative solution based on this blueprint:
                {blueprint}
                Use clear variable names and explicit loops. Handle all edge cases mentioned.
                Return EXACTLY the required data type. Include necessary imports inside function if needed.""",
                context=blueprint
            ),
            self.generate(
                instruction=f"""Generate a functional/declarative solution using map/filter/reduce or comprehensions:
                {blueprint}
                Prioritize readability and Pythonic style. Still handle all edge cases.
                Ensure return type matches specification exactly.""",
                context=blueprint
            ),
            self.generate(
                instruction=f"""Generate an optimized or mathematical solution (if applicable):
                {blueprint}
                Look for formulaic approaches, built-in functions, or library solutions (like regex).
                Only if appropriate for the problem type. Still maintain edge case handling.""",
                context=blueprint
            )
        )

        # Step 4: Validate each solution against requirements
        validations = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically validate this solution against the blueprint:
                Blueprint: {blueprint}
                
                Check for:
                1. Correct handling of all specified edge cases
                2. Exact match of required return type
                3. Adherence to transformation rules
                4. No extraneous operations or assumptions
                5. Proper import statements (if any) placed correctly
                
                If any issues found, describe them specifically. If perfect, say 'VALIDATED'.""",
                context=sol
            ) for sol in solution_attempts]
        )

        # Step 5: Select or synthesize best solution
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness (validated solutions preferred)
            2. Simplicity and readability
            3. Efficiency (avoid unnecessary complexity)
            4. Strict adherence to return type and edge cases
            
            If multiple are validated, choose the most elegant.
            If none fully validated, synthesize a corrected version combining strengths.
            Return ONLY the raw Python function code - no explanations, no markdown.""",
            contexts_list=[f"Solution: {sol}\nValidation: {val}" for sol, val in zip(solution_attempts, validations)]
        )

        # Step 6: Final refinement - extract pure function code
        final_code = await self.revise(
            instruction="""Extract ONLY the Python function implementation from the following text.
            Remove all explanations, comments, markdown formatting, and extra text.
            Ensure:
            - Function has exact name and signature as required
            - All imports are inside the function if needed
            - Return statement matches required type
            - No wrapper code or additional functions
            Return raw code ready for execution.""",
            context=selected_solution
        )

        return final_code