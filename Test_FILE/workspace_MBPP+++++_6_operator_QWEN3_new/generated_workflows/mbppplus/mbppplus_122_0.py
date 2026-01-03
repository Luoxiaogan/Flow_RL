# Workflow ID: mbppplus_122_0
# Benchmark: mbppplus
# Data Indices: [204, 35]

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

        # Phase 1: Problem Classification & Edge Case Identification
        classification = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify problem type: mathematical, logical, collection-based, string, or other.
            2. Identify input/output data structures and expected types (list, tuple, set, scalar).
            3. Extract implicit constraints from examples (e.g., order preservation, mutability).
            4. Enumerate ALL edge cases: empty inputs, single elements, duplicates, type boundaries, zero/negative values.
            5. Infer the core operation: aggregation, filtering, transformation, comparison, or validation.
            6. Determine if solution requires built-in functions (max, sum, any) or custom logic.
            Format as structured JSON-like outline with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Hypothesis Generation
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Hypothesis A (Literal Pattern):
                Based on classification: {classification}
                - Directly extrapolate from given test cases.
                - Implement minimal logic that satisfies visible examples.
                - Prioritize simplicity and directness.
                - Include handling for identified edge cases.
                Output ONLY the function implementation with exact signature.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis B (Algorithmic/Idiomatic):
                Based on classification: {classification}
                - Use optimal Python idioms and built-ins (e.g., max with key, set operations).
                - Focus on efficiency and elegance.
                - Ensure type consistency and edge case robustness.
                - Consider functional programming approaches if applicable.
                Output ONLY the function implementation with exact signature.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate Solution Hypothesis C (Defensive/Explicit):
                Based on classification: {classification}
                - Implement with explicit conditionals and guards.
                - Handle all edge cases with dedicated branches.
                - Prioritize readability and maintainability.
                - Include type checks and assertions if appropriate.
                Output ONLY the function implementation with exact signature.""",
                context=classification
            )
        )

        # Phase 3: Solution Synthesis & Cross-Validation
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these hypotheses:
            - Compare for correctness, robustness, and elegance.
            - Merge strengths: take idiomatic efficiency from B, edge case handling from C, simplicity from A.
            - Ensure exact function signature and return type matching.
            - Eliminate any print statements, extra text, or wrapper code.
            - Output ONLY the final function implementation, nothing else.
            - If conflicts exist, prioritize correctness and edge case coverage over brevity.""",
            contexts_list=solution_hypotheses
        )

        # Phase 4: Validation-Driven Refinement Loop
        refined_solution = synthesized_solution
        for iteration in range(3):  # Max 3 refinement rounds
            validation_feedback = await self.generate(
                instruction=f"""Critique this implementation:
                {refined_solution}
                
                Check against:
                1. Problem classification: {classification}
                2. Edge cases identified earlier
                3. Type consistency (list vs tuple vs set)
                4. Signature compliance (exact parameter names, return type)
                5. Potential failures: empty inputs, type errors, boundary conditions
                6. Code cleanliness (no extra prints, imports in correct location)
                
                If perfect, respond "VALID". Otherwise, provide specific, actionable fixes.""",
                context=refined_solution
            )
            
            if "VALID" in validation_feedback.upper():
                break
                
            refined_solution = await self.revise(
                instruction=f"""Revise the implementation based on this feedback:
                {validation_feedback}
                
                Requirements:
                - Fix ALL identified issues.
                - Preserve function signature exactly.
                - Return ONLY the function code, no explanations.
                - Ensure imports are inside function if needed.
                - Handle all edge cases from classification: {classification}""",
                context=refined_solution
            )

        # Final Output Enforcement
        final_clean = await self.revise(
            instruction="""Ensure this is PERFECT for submission:
            - ONLY the function implementation, nothing before or after.
            - Exact function name and parameters as in problem.
            - All necessary imports inside function body.
            - No type hints unless specified in original signature.
            - No extra whitespace or comments unless part of logic.
            - Return type matches exactly what tests expect.
            If already perfect, return unchanged. Otherwise, clean precisely.""",
            context=refined_solution
        )

        return final_clean