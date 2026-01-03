# Workflow ID: limr_166_0
# Benchmark: limr
# Data Indices: [92, 0]

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
        import json

        # PHASE 1: PROBLEM ANATOMY & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. List all variables, constants, and constraints explicitly stated or implied
            3. Determine if the problem requires exact computation, proof, optimization, or counting
            4. Note any symmetries, invariants, or patterns in the equations or conditions
            5. Assess whether multiple solutions are possible or if edge cases exist
            6. Estimate computational complexity if brute-force approach were attempted
            7. Suggest 2-3 potential solution strategies ranked by likely efficiency
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION (DIAMOND PATTERN)
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a complete solution using ALGEBRAIC MANIPULATION:
                - Transform equations to isolate variables or exploit symmetry
                - Use substitution, elimination, or factorization as appropriate
                - Track all constraints and verify solution validity at each step
                - Present final answer as integer(s) between 000-999, comma-separated if multiple
                Base your approach on this analysis: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop a complete solution using COMPUTATIONAL/PROGRAMMATIC APPROACH:
                - Identify what needs to be calculated, iterated, or simulated
                - Define bounds, step sizes, or termination conditions
                - Consider edge cases and numerical precision requirements
                - Present final answer as integer(s) between 000-999, comma-separated if multiple
                Base your approach on this analysis: {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop a complete solution using GEOMETRIC/COMBINATORIAL REASONING:
                - Interpret equations or conditions as geometric relationships or counting problems
                - Apply principles like inclusion-exclusion, pigeonhole, or coordinate transformations
                - Use diagrams or spatial reasoning if applicable
                - Present final answer as integer(s) between 000-999, comma-separated if multiple
                Base your approach on this analysis: {problem_analysis}""",
                context=problem_analysis
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # PHASE 3: VALIDATION & REFINEMENT CASCADE
        validated_strategies = []
        for i, strategy in enumerate(strategy_results):
            validation = await self.generate(
                instruction=f"""Critically validate this solution attempt:
                1. Check all mathematical steps for logical consistency and arithmetic accuracy
                2. Verify that the solution satisfies ALL original problem constraints
                3. Test edge cases or boundary conditions mentioned in problem analysis
                4. Flag any assumptions that may not hold universally
                5. If errors found, suggest specific corrections
                Return 'VALID' if flawless, otherwise return 'INVALID: [reason]'""",
                context=strategy
            )
            
            if "VALID" in validation:
                validated_strategies.append(strategy)
            else:
                # Revise and re-validate once
                revised = await self.revise(
                    instruction=f"""Correct all errors identified in validation: {validation}
                    Maintain the original solution structure but fix logical/mathematical flaws.
                    Ensure final answer format is integer(s) 000-999, comma-separated if multiple.""",
                    context=strategy
                )
                # Quick re-validation
                revalidation = await self.generate(
                    instruction="Final check: Does this revised solution satisfy all constraints? Answer only 'YES' or 'NO'",
                    context=revised
                )
                if "YES" in revalidation:
                    validated_strategies.append(revised)
                else:
                    # Fallback: mark as unvalidated but keep for ensemble consideration
                    validated_strategies.append(strategy)

        # PHASE 4: ENSEMBLE SYNTHESIS & FINAL VERIFICATION
        if len(validated_strategies) == 0:
            # Emergency fallback: use raw strategies
            final_answer = await self.ensemble(
                instruction="""Select the most mathematically rigorous solution from candidates.
                Prioritize solutions that:
                - Explicitly verify against original constraints
                - Show complete step-by-step reasoning
                - Handle edge cases appropriately
                - Produce integer answer(s) in 000-999 range
                If consensus exists among multiple solutions, that is preferred.
                Return ONLY the final answer(s) as integers, comma-separated if multiple.""",
                contexts_list=strategy_results
            )
        else:
            final_answer = await self.ensemble(
                instruction="""Synthesize the validated solutions into a final answer.
                Look for consensus among valid solutions.
                If disagreement exists, select the solution with the most thorough verification.
                Return ONLY the final answer(s) as integers between 000-999, comma-separated if multiple.
                Do not include any explanation or working.""",
                contexts_list=validated_strategies
            )

        # PHASE 5: COMPUTATIONAL VERIFICATION (if applicable)
        # Extract potential numerical answer for verification
        verification_context = f"Proposed answer: {final_answer}

Problem analysis: {problem_analysis}"
        
        computational_check = await self.programmer(
            instruction=f"""Verify the proposed answer computationally:
            - If the answer is a single integer or list of integers, plug back into original equations/conditions
            - Check if all constraints are satisfied
            - For inequalities, verify boundary conditions
            - For counting problems, validate with small cases if possible
            - Return 'VERIFIED' if correct, 'ERROR: [description]' if incorrect
            - If computational verification is not applicable, return 'NOT_APPLICABLE'""",
            context=verification_context
        )

        if "VERIFIED" not in computational_check and "NOT_APPLICABLE" not in computational_check:
            # Final fallback: recompute from scratch using programmer
            direct_computation = await self.programmer(
                instruction="""Solve the original problem computationally from first principles:
                - Parse all equations, inequalities, or conditions
                - Implement algorithm to find all valid integer solutions in 000-999 range
                - Handle edge cases and boundary conditions
                - Return ONLY the answer(s) as integers, comma-separated if multiple""",
                context=""
            )
            return direct_computation

        return final_answer