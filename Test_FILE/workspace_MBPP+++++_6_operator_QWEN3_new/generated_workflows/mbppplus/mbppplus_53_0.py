# Workflow ID: mbppplus_53_0
# Benchmark: mbppplus
# Data Indices: [145, 21]

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
        import json

        # PHASE 1: PROBLEM DISCOVERY & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the programming problem. Identify:
            1. Problem category (mathematical, algorithmic, data structure, string manipulation, logical)
            2. Input types and expected output type
            3. Key constraints and edge cases (empty inputs, boundaries, special values)
            4. Known algorithmic patterns or formulas that might apply
            5. Potential failure points in naive implementations
            Structure your response as a detailed, categorized analysis.""",
            context=""
        )

        # PHASE 2: STRATEGY GENERATION (PARALLEL)
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Propose a solution strategy focusing on DIRECT FORMULA APPLICATION.
                - Identify any mathematical formulas or closed-form solutions
                - Specify how to handle edge cases explicitly
                - Outline step-by-step computation""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Propose a solution strategy focusing on ITERATIVE/ALGORITHMIC APPROACH.
                - Describe the algorithm step by step
                - Specify data structures and control flow
                - Address edge cases and termination conditions""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Propose a solution strategy focusing on LIBRARY/UTILITY FUNCTIONS.
                - Identify any built-in Python functions or standard library modules that could help
                - Describe how to compose them for the solution
                - Note any limitations or edge case handling required""",
                context=problem_analysis
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # PHASE 3: STRATEGY SELECTION
        selected_strategy = await self.ensemble(
            instruction="""Evaluate these solution strategies and select the optimal one.
            Criteria:
            1. Correctness: Does it handle all edge cases identified in the analysis?
            2. Efficiency: Is it computationally appropriate for the problem scale?
            3. Simplicity: Is it straightforward to implement without unnecessary complexity?
            4. Robustness: Does it include explicit error handling or input validation?
            Provide a detailed justification for your selection and output only the chosen strategy.""",
            contexts_list=strategy_candidates
        )

        # PHASE 4: SOLUTION GENERATION (PARALLEL VARIANTS)
        solution_variants = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a detailed solution description based on this strategy: {selected_strategy}
                Focus: MAXIMUM CLARITY
                - Use simple, explicit steps
                - Include comments for each logical block
                - Name variables descriptively
                - Handle edge cases with early returns""",
                context=selected_strategy
            ),
            self.generate(
                instruction=f"""Generate a detailed solution description based on this strategy: {selected_strategy}
                Focus: EDGE CASE ROBUSTNESS
                - Explicitly check all boundary conditions
                - Validate input types and ranges
                - Include defensive programming practices
                - Handle empty, single-element, and extreme value cases""",
                context=selected_strategy
            ),
            self.generate(
                instruction=f"""Generate a detailed solution description based on this strategy: {selected_strategy}
                Focus: PERFORMANCE OPTIMIZATION
                - Minimize time/space complexity
                - Avoid redundant computations
                - Use efficient data structures
                - Consider early termination opportunities""",
                context=selected_strategy
            )
        )

        # PHASE 5: SOLUTION VALIDATION & SYNTHESIS
        validation_tasks = [
            self.revise(
                instruction="""Critique this solution for:
                1. Logical correctness - are there any flaws in the reasoning?
                2. Edge case coverage - are all boundary conditions handled?
                3. Type consistency - does it match expected input/output types?
                4. Implementation feasibility - can this be directly coded?
                Provide specific, actionable improvements.""",
                context=variant
            ) for variant in solution_variants
        ]
        
        validated_solutions = await asyncio.gather(*validation_tasks)

        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all validated solutions into one master solution description.
            Rules:
            1. Prioritize correctness and edge case handling above all else
            2. Incorporate clarity improvements where they don't compromise robustness
            3. Add performance optimizations only if they don't introduce complexity or risk
            4. Ensure the solution can be directly translated to code with the exact function signature
            Output a comprehensive, step-by-step solution ready for implementation.""",
            contexts_list=validated_solutions
        )

        # PHASE 6: CODE GENERATION & REFINEMENT
        final_code = None
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                code_result = await self.programmer(
                    instruction=f"""Generate Python code that implements this solution: {synthesized_solution}
                    Requirements:
                    - Use EXACT function name and signature from the original problem
                    - Include all necessary imports at the top of the function
                    - Handle all edge cases explicitly (return None, raise exceptions, etc. as appropriate)
                    - Match expected return types precisely (list vs tuple vs set)
                    - Include brief comments explaining key decisions
                    - Prioritize readability and robustness over cleverness
                    - Do NOT wrap in any outer function or class - output only the function implementation""",
                    context=synthesized_solution,
                    max_retries=1
                )
                
                # Extract just the code portion (assuming programmer returns code in markdown block)
                code_match = re.search(r'