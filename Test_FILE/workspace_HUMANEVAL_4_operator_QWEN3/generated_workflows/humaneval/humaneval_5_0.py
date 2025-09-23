# Workflow ID: humaneval_5_0
# Benchmark: humaneval
# Data Indices: [60, 1]

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

        # Phase 1: Deep Problem Analysis & Classification
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this code generation problem. Your analysis must include:
            1. Problem Type Classification: Is this mathematical, string manipulation, list processing, algorithmic, or pattern-based?
            2. Key Constraints: What are the explicit and implicit constraints from the examples? (e.g., return type, edge cases, performance)
            3. Pattern Extraction: What is the underlying pattern or formula demonstrated by the examples?
            4. Edge Case Identification: What edge cases must be handled? (consider empty inputs, zeros, negatives, boundaries)
            5. Solution Strategy: What approach should be used? (formula, iteration, recursion, regex, stack, etc.)
            6. Return Type Specification: Must output be int, float, list, string? Be precise.
            Format your response as a structured JSON-like block with these 6 sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation with Different Strategies
        solution_strategies = [
            "Generate a direct, minimal implementation focusing on mathematical elegance and formula usage if applicable.",
            "Generate an iterative, step-by-step implementation that explicitly handles all edge cases mentioned in analysis.",
            "Generate a functional-style solution using built-ins and comprehensions, optimized for readability and conciseness."
        ]

        solution_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on this analysis:
                {analysis}
                
                {strategy} 
                - Function name must match ENTRY POINT exactly.
                - Return type must match examples precisely.
                - Handle all identified edge cases.
                - No over-engineering: implement exactly what's specified.
                - If imports are needed (e.g., re, math), include them inline.
                Output ONLY the function definition with no additional text.""",
                context=analysis
            ) for strategy in solution_strategies]
        )

        # Phase 3: Adversarial Validation - Generate Edge Case Tests
        validator_prompt = f"""You are a ruthless code validator. Based on the problem analysis:
        {analysis}
        
        For each of the following candidate solutions, generate 3-5 edge case test scenarios that could break it.
        Focus on: type mismatches, off-by-one errors, empty/zero/negative inputs, performance traps, and specification violations.
        Format each test as: "Input: X, Expected: Y, Why: Z"
        """
        
        validation_scenarios = await asyncio.gather(
            *[self.generate(
                instruction=validator_prompt,
                context=candidate
            ) for candidate in solution_candidates]
        )

        # Phase 4: Revise Candidates Based on Validation Feedback
        revised_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"""Revise this code to handle the following edge cases:
                {validation}
                
                - Preserve the original functionality.
                - Fix only what's necessary.
                - Maintain exact function signature and return type.
                - Output ONLY the revised function definition.""",
                context=candidate
            ) for candidate, validation in zip(solution_candidates, validation_scenarios)]
        )

        # Phase 5: Ensemble Selection with Logical Consistency Check
        final_selection = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Must handle all edge cases from validation.
            2. Simplicity: Minimal, readable, no unnecessary complexity.
            3. Efficiency: Optimal time/space complexity for the problem type.
            4. Specification Compliance: Exact match to examples and return types.
            5. Robustness: Least likely to fail on hidden test cases.
            
            If multiple solutions are equally good, prefer the most mathematically elegant or algorithmically efficient.
            Output ONLY the selected function definition with no additional text.""",
            contexts_list=revised_candidates
        )

        # Phase 6: Final Safety Check and Type Enforcement
        final_code = await self.revise(
            instruction=f"""Perform a final safety check:
            - Ensure function name matches ENTRY POINT exactly.
            - Verify return type matches examples (int vs float matters).
            - Confirm no imports are missing if used.
            - Remove any debug prints or extra comments.
            - Output ONLY the clean function definition.
            
            Problem Analysis for reference:
            {analysis}""",
            context=final_selection
        )

        return final_code