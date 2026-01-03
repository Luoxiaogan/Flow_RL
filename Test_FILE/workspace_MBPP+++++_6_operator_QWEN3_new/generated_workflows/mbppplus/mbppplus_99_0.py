# Workflow ID: mbppplus_99_0
# Benchmark: mbppplus
# Data Indices: [250, 17]

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

        # Step 1: Problem Classification and Intent Extraction
        classification = await self.generate(
            instruction="""Analyze the problem statement with extreme care. Your task is not to solve it yet, but to understand its essence.

            1. Classify the problem type: Is it mathematical (algebraic, arithmetic), algorithmic (data processing, transformations), logical (conditionals, validations), or structural (data type conversions)?
            2. Extract key variables and their roles. What are the inputs? What is the expected output? What hidden constraints might exist?
            3. Identify potential misdirections: Are there terms in the problem name that don't match the actual solution (e.g., 'inverse divisors' that aren't actually about divisors)?
            4. Infer the return type from test cases: Is it float, int, list, tuple? Must order be preserved?
            5. List all edge cases you can anticipate: empty inputs, zeros, negatives, single elements, duplicates, type mismatches.
            6. Confidence assessment: How certain are you about this classification? (High/Medium/Low)

            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Parallel Solution Hypothesis Generation
        # Generate three different solution approaches in parallel
        hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the classification:
                {classification}

                Generate Solution Hypothesis 1: Assume this is a direct mathematical transformation. Ignore any complex-sounding terms in the problem name. Look for algebraic relationships between inputs and outputs. Provide the mathematical formula that would solve this, with step-by-step derivation.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on the classification:
                {classification}

                Generate Solution Hypothesis 2: Assume this requires algorithmic processing (loops, iterations, data structure operations). Break down the steps needed to transform inputs to outputs. Consider edge cases explicitly in your algorithm design.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on the classification:
                {classification}

                Generate Solution Hypothesis 3: Assume this is a trick question where the solution is simpler than it appears. Look for patterns in the test cases. Is there a direct mapping or identity that bypasses complex computation?""",
                context=classification
            )
        )

        # Step 3: Solution Synthesis via Ensemble
        synthesized_approach = await self.ensemble(
            instruction="""You are given three different solution hypotheses for the same problem. Your task is to synthesize the best possible approach.

            Evaluation Criteria:
            1. Mathematical Consistency: Does the solution align with the test cases?
            2. Simplicity: Prefer algebraic identities over complex algorithms unless complexity is unavoidable.
            3. Edge Case Coverage: Does the solution handle all anticipated edge cases?
            4. Type Safety: Does it respect the expected return type and data structure?

            Synthesize a unified solution specification that:
            - States the core mathematical or logical relationship
            - Lists all edge cases that must be handled
            - Specifies the exact return type and format
            - Provides the minimal necessary steps to implement

            If hypotheses conflict, resolve by testing against the provided test cases mentally. Choose the hypothesis that best fits all test cases with minimal complexity.""",
            contexts_list=hypotheses
        )

        # Step 4: Code Generation with Edge Case Awareness
        initial_code = await self.programmer(
            instruction=f"""Implement the function as specified below. You MUST handle all edge cases mentioned in the synthesis.

            Synthesized Specification:
            {synthesized_approach}

            Implementation Requirements:
            - Use the EXACT function signature from the problem
            - Include all necessary imports
            - Handle edge cases explicitly (empty inputs, zeros, negatives, etc.)
            - Return the correct data type (float, int, list, etc.) as inferred
            - Round to specified decimal places if mentioned
            - Do NOT include any print statements or interactive code
            - Code must be production-ready and pass all test cases

            IMPORTANT: If the problem involves division, check for division by zero. If it involves lists, check for empty lists. Be defensively programmed.""",
            context=synthesized_approach
        )

        # Step 5: Iterative Validation and Refinement (up to 3 attempts)
        current_code = initial_code
        for attempt in range(3):
            validation = await self.revise(
                instruction=f"""You are a ruthless code validator. Critically examine this implementation:

                {current_code}

                Against the original problem and synthesized specification:
                {synthesized_approach}

                Check for:
                1. Correctness: Does it match the mathematical/logical relationship?
                2. Edge Cases: Are all edge cases from the synthesis handled?
                3. Type Safety: Correct return type? Proper handling of input types?
                4. Robustness: Any potential runtime errors (division by zero, index out of bounds, etc.)?
                5. Precision: Correct rounding? Floating point issues?

                If any issues are found, provide a detailed critique and specific instructions for fixing them.
                If no issues are found, respond with 'VALIDATED: No issues found.'""",
                context=current_code
            )

            if "VALIDATED" in validation and "No issues found" in validation:
                break
            else:
                # Revise code based on validation feedback
                current_code = await self.programmer(
                    instruction=f"""Revise the following code to fix all issues identified in the validation:

                    Validation Feedback:
                    {validation}

                    Original Synthesized Specification:
                    {synthesized_approach}

                    Requirements:
                    - Maintain the exact function signature
                    - Fix all identified issues
                    - Preserve all previously handled edge cases
                    - Return code only, no explanations""",
                    context=current_code
                )

        # Step 6: Final Code Extraction and Cleanup
        # Extract just the code block from the final output
        code_lines = current_code.split('\n')
        final_code_lines = []
        in_code_block = False
        
        for line in code_lines:
            if line.strip().startswith('