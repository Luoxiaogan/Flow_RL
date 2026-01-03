# Workflow ID: humaneval_48_0
# Benchmark: humaneval
# Data Indices: [52, 5]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for generating Python functions from docstring specifications.
        Dynamically classifies problem type, generates multiple solution perspectives,
        self-validates against examples, and ensures strict compliance with signature.
        """
        import asyncio

        # Phase 1: Deep Problem Analysis & Classification
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the given function specification and docstring examples. Extract:
            1. The core task: What transformation or check is being performed?
            2. Input types and structures (list, int, string, etc.)
            3. Output type and format (must match examples exactly - int vs float matters)
            4. Edge cases implied by examples (empty inputs, single elements, boundary values)
            5. Comparison logic (e.g., < vs <=, exact matches, etc.)
            6. Any hidden constraints or assumptions
            Present as a structured breakdown with clear headings.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        # Fork into three independent reasoning paths
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}

                Derive the core algorithmic logic. Focus on:
                - Step-by-step procedure to transform input to output
                - Loop structures or functional patterns needed
                - Conditional checks and their exact conditions
                - How to handle the edge cases identified
                Output only the algorithmic steps in clear, imperative language.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}

                Focus exclusively on return type and signature compliance:
                - What exact data type must be returned? (Infer from examples)
                - Are there type conversions needed?
                - Must the function handle mixed types? 
                - Verify function name matches ENTRY POINT exactly
                Output a strict type and signature compliance checklist.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}

                Identify all edge cases and boundary conditions:
                - Empty inputs
                - Single element inputs
                - Maximum/minimum values
                - Duplicate values
                - Type edge cases (e.g., 0, negative numbers, None)
                For each, specify the expected behavior and how to handle it in code.
                Format as a bullet-point list with 'Edge Case: [description] -> Expected: [behavior]'.""",
                context=problem_analysis
            )
        ]

        # Execute parallel analysis
        algorithm_logic, type_compliance, edge_cases = await asyncio.gather(*strategy_tasks)

        # Phase 3: Synthesize into Implementation Strategy
        implementation_strategy = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified implementation plan:
            1. Combine algorithmic logic with edge case handling
            2. Integrate type and signature requirements
            3. Ensure minimal, clean code - no over-engineering
            4. Specify exact variable names and control flow
            5. Include explicit handling for each edge case
            Output a complete, line-by-line pseudocode implementation that satisfies all requirements.""",
            contexts_list=[algorithm_logic, type_compliance, edge_cases]
        )

        # Phase 4: Generate Initial Code Draft
        initial_code = await self.generate(
            instruction=f"""Generate the final Python function based on this implementation strategy:
            {implementation_strategy}

            STRICT REQUIREMENTS:
            - Function name MUST exactly match the ENTRY POINT
            - Return type MUST match examples precisely (int vs float)
            - Handle all edge cases identified
            - Code must be minimal - no extra imports or logic
            - Use clear, Pythonic style
            - Include NO comments or docstrings - just the function body
            - If imports are needed, they will be added automatically - do not include them

            Output ONLY the function definition and body, nothing else.""",
            context=implementation_strategy
        )

        # Phase 5: Self-Validation and Refinement Loop (up to 2 iterations)
        current_code = initial_code
        for iteration in range(2):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this code against the original specification and examples:
                Code:
                {current_code}

                Check:
                1. Does it handle all example cases correctly?
                2. Are edge cases properly addressed?
                3. Is return type exact match?
                4. Is function name correct?
                5. Any logical errors or off-by-one mistakes?
                6. Any unnecessary complexity?

                If perfect, respond with 'VALIDATED'. Otherwise, provide specific, line-by-line corrections needed.""",
                context=current_code
            )

            if "VALIDATED" in validation_feedback.upper():
                break

            # Revise based on feedback
            current_code = await self.revise(
                instruction=f"""Revise the code based on this feedback:
                {validation_feedback}

                Make ONLY the necessary changes. Preserve correct parts.
                Maintain minimal, clean implementation.
                Ensure function name and return type remain correct.""",
                context=current_code
            )

        # Phase 6: Final Compliance Check
        final_code = await self.revise(
            instruction="""Final compliance check:
            1. Ensure function definition starts exactly with 'def [ENTRY POINT NAME]('
            2. No extra imports or comments
            3. Code is as minimal as possible
            4. Return statements match example types exactly
            5. All edge cases from analysis are handled

            Make ONLY mechanical corrections if needed. Do not change logic unless absolutely necessary.""",
            context=current_code
        )

        return final_code