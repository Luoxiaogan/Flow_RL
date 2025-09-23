# Workflow ID: mbppplus_165_0
# Benchmark: mbppplus
# Data Indices: [89, 141]

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

        # Step 1: Parallel problem classification from multiple perspectives
        classification_promises = [
            self.generate(
                instruction="""Analyze this problem from a mathematical perspective:
                - Identify if it involves numerical computation, formulas, or equations
                - Determine if it requires exact calculation or can use approximations
                - Note any mathematical constants or functions needed (sqrt, log, etc.)
                - Output format: 'Math: [summary]'""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a data structure perspective:
                - Identify if it involves lists, tuples, strings, sets, or dictionaries
                - Determine operations needed: iteration, indexing, slicing, filtering, etc.
                - Note any constraints on order, duplicates, or mutability
                - Output format: 'Data: [summary]'""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from an edge case perspective:
                - Identify potential edge cases: empty inputs, single elements, zeros, negatives
                - Determine boundary conditions and special values
                - Note any type conversion or validation requirements
                - Output format: 'Edge: [summary]'""",
                context=""
            )
        ]
        
        classification_results = await asyncio.gather(*classification_promises)
        unified_classification = await self.ensemble(
            instruction="""Synthesize these three analyses into a unified problem classification.
            Identify the dominant problem type and key requirements.
            Format as: 'Type: [main_type]. Key: [comma_separated_key_points]'""",
            contexts_list=classification_results
        )

        # Step 2: Determine complexity and decide whether to decompose
        complexity_analysis = await self.generate(
            instruction=f"""Based on this classification: {unified_classification}
            Assess problem complexity:
            - Can it be solved with a single expression or built-in function? (Simple)
            - Does it require iteration or simple loops? (Moderate)
            - Does it require multi-step reasoning, recursion, or complex algorithms? (Complex)
            Output only one word: 'Simple', 'Moderate', or 'Complex'""",
            context=unified_classification
        )

        # Step 3: Generate solution approach - parallel sketches then ensemble
        if "Complex" in complexity_analysis:
            # Decompose for complex problems
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, independent subproblems.
                Each subproblem should be solvable in isolation.
                Avoid circular dependencies. Prioritize base cases first.""",
                context=unified_classification
            )
            decomposition_summary = await self.summarize(
                instruction="Convert decomposition into a concise, numbered list of steps",
                context=str(decomposition)
            )
            solution_context = f"Classification: {unified_classification}\nDecomposition: {decomposition_summary}"
        else:
            solution_context = f"Classification: {unified_classification}"

        # Generate multiple solution sketches in parallel
        solution_sketches = await asyncio.gather(
            self.generate(
                instruction=f"""Based on context: {solution_context}
                Generate a Python solution sketch. Focus on core logic.
                Include key variables and control flow. Skip edge case handling for now.
                Format as code comments describing the approach.""",
                context=solution_context
            ),
            self.generate(
                instruction=f"""Based on context: {solution_context}
                Generate an alternative Python solution sketch. Consider different algorithms or data structures.
                Focus on efficiency and simplicity. Format as code comments.""",
                context=solution_context
            ),
            self.generate(
                instruction=f"""Based on context: {solution_context}
                Generate a defensive solution sketch. Focus on edge cases and error handling.
                Include input validation and boundary condition checks. Format as code comments.""",
                context=solution_context
            )
        )

        # Ensemble the sketches into a unified solution specification
        solution_spec = await self.ensemble(
            instruction="""Merge these solution sketches into one comprehensive specification.
            Include: core algorithm, edge case handling, input validation, and efficiency considerations.
            Format as a detailed, step-by-step recipe for implementation.""",
            contexts_list=solution_sketches
        )

        # Step 4: Generate and refine code with iterative error correction
        max_attempts = 3
        final_code = None
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                if last_error:
                    # Revise approach based on previous error
                    revised_spec = await self.revise(
                        instruction=f"""Previous attempt failed with error: {last_error}
                        Revise the solution specification to fix this error.
                        Consider alternative approaches or additional validation.
                        Maintain all previous requirements.""",
                        context=solution_spec
                    )
                    current_spec = revised_spec
                else:
                    current_spec = solution_spec

                # Generate code with explicit edge case instructions
                code_result = await self.programmer(
                    instruction=f"""Implement this solution: {current_spec}
                    MUST handle all edge cases identified in classification.
                    Return ONLY the function with exact signature from problem.
                    Include necessary imports. No test cases or explanations.
                    Ensure type consistency and return type matches problem requirements.""",
                    context=current_spec,
                    max_retries=1
                )
                
                # Extract just the code portion (Programmer returns more than just code)
                code_match = re.search(r'