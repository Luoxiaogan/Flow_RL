# Workflow ID: mbppplus_10_0
# Benchmark: mbppplus
# Data Indices: [134, 234, 38]

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

        # STEP 1: Problem Classification & Contract Generation
        classification = await self.generate(
            instruction="""Analyze the problem and classify it into one of these categories: 
            [Mathematical, String Processing, Bit Manipulation, Data Structure, Logical Validation].
            Then, extract the following:
            1. Expected function signature (name and parameters)
            2. Return type (int, float, list, tuple, bool, etc.)
            3. Obvious edge cases (empty input, single element, zero, negatives, etc.)
            4. Hidden constraints (order preservation, mutation rules, etc.)
            5. Performance hints (if any)
            Format as structured JSON with keys: category, signature, return_type, edge_cases, constraints, performance.
            Be conservative — if unsure, include more edge cases.""",
            context=""
        )

        # STEP 2: Parallel Solution Generation (3 strategies)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct solution based on the problem's apparent intent.
                Use the classification: {classification}
                Prioritize clarity and correctness. Include type handling and edge case guards.
                Return ONLY the function implementation as specified in the signature.
                Do not include explanations or markdown.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a defensive solution that over-engineers edge case handling.
                Based on classification: {classification}
                Assume worst-case inputs. Add explicit guards for type, length, division-by-zero, etc.
                Return ONLY the function implementation. No comments or explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a minimal, mathematically/optimal solution.
                Based on classification: {classification}
                Use bit operations, algebraic simplifications, or algorithmic optimizations where possible.
                Sacrifice readability for correctness and efficiency if needed.
                Return ONLY the function implementation.""",
                context=""
            )
        )

        # STEP 3: Ensemble Synthesis with Edge Case Injection
        synthesized = await self.ensemble(
            instruction=f"""Synthesize the best solution from these attempts:
            {solution_attempts}
            
            CRITICAL RULES:
            1. Preserve the exact function signature from classification.
            2. Incorporate edge case handling from the defensive version.
            3. Prefer mathematical elegance from the minimal version if correct.
            4. If return type is ambiguous, default to the most restrictive (e.g., int over float).
            5. Handle empty inputs unless explicitly forbidden.
            6. NEVER change parameter names or function name.
            
            Output ONLY the final function implementation. No markdown, no explanations.""",
            contexts_list=solution_attempts
        )

        # STEP 4: Iterative Validation & Refinement (max 2 iterations)
        current_solution = synthesized
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {current_solution}
                
                Check against:
                1. Function signature compliance
                2. Return type correctness
                3. Edge cases from classification: {classification}
                4. Type stability (no silent conversions)
                5. Division-by-zero, index-out-of-bounds, etc.
                
                If valid, output "VALID". Otherwise, describe EXACTLY what's wrong in 1-2 sentences.
                Be specific: "Fails on empty list input", "Returns list instead of tuple", etc.""",
                context=current_solution
            )
            
            if "VALID" in validation.upper():
                break
                
            # Revise with specific feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix this specific issue:
                {validation}
                
                Maintain all other correct behavior. Do not introduce new bugs.
                Return ONLY the corrected function implementation. No explanations.""",
                context=current_solution
            )
        else:
            # Final fallback: choose the most defensive version if still failing
            current_solution = solution_attempts[1]  # Defensive version

        return current_solution