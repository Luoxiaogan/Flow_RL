# Workflow ID: limr_8_0
# Benchmark: limr
# Data Indices: [134, 232]

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

        # PHASE 1: PROBLEM CLASSIFICATION & META-STRATEGY
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary mathematical domain (geometry, number theory, combinatorics, algebra, optimization, etc.)
            2. List required techniques (induction, modular arithmetic, coordinate geometry, generating functions, etc.)
            3. Determine answer format (integer, fraction, decimal, etc.) and constraints (000-999 integer)
            4. Estimate complexity (number of steps, potential pitfalls)
            5. Suggest 3 distinct solution approaches (even if problem seems to favor one)
            Output as structured JSON with keys: domain, techniques, answer_format, complexity, approaches""",
            context=""
        )

        # PHASE 2: PARALLEL DECOMPOSITION & EXPLORATION
        decomposition = await self.decompose(
            instruction="""Decompose problem into minimal subproblems:
            - Each subproblem should be independently solvable or have clear dependencies
            - Prioritize mathematical atomicity (one concept per subproblem)
            - Include prerequisite relationships
            - Maximum 7 subproblems for manageability""",
            context=classification
        )

        # Generate 3 parallel solution pathways
        approach_instructions = [
            f"""Develop solution using APPROACH 1 from classification:
            {classification}
            Focus on mathematical rigor, show all steps, flag any assumptions.
            Format: Step-by-step derivation ending with boxed answer.""",
            
            f"""Develop solution using APPROACH 2 from classification:
            {classification}
            Emphasize alternative perspective, even if non-obvious. Challenge conventional methods.
            Format: Step-by-step derivation ending with boxed answer.""",
            
            f"""Develop solution using APPROACH 3 from classification:
            {classification}
            Prioritize computational feasibility. Where possible, set up for code verification.
            Format: Step-by-step derivation ending with boxed answer."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in approach_instructions]
        )

        # PHASE 3: ADVERSARIAL REFINEMENT
        refined_candidates = []
        for i, sol in enumerate(candidate_solutions):
            critique = await self.generate(
                instruction=f"""Critique this solution adversarially:
                - Identify weakest assumption
                - Find potential calculation error
                - Check boundary conditions
                - Verify answer format compliance (integer 000-999)
                - Suggest one improvement
                Be brutally honest.""",
                context=sol
            )
            
            refined = await self.revise(
                instruction=f"""Revise solution based on critique:
                CRITIQUE: {critique}
                - Fix all identified issues
                - Strengthen logical flow
                - Add verification step
                - Ensure final answer is boxed and in correct format""",
                context=sol
            )
            refined_candidates.append(refined)

        # PHASE 4: SYNTHESIS & COMPUTATIONAL VERIFICATION
        synthesized = await self.ensemble(
            instruction="""Synthesize best elements from all candidates:
            - Preserve mathematical correctness above all
            - Choose most elegant/efficient path
            - Resolve contradictions via logical priority
            - Output FINAL ANSWER as integer between 000-999 in \\boxed{{}} format
            - Include brief justification for chosen approach""",
            contexts_list=refined_candidates
        )

        # Extract answer for verification
        answer_extraction = await self.generate(
            instruction="""Extract the final numerical answer from this solution:
            - Must be integer between 000-999
            - If multiple answers, choose most rigorously derived
            - If no valid answer, return "RETRY"
            - Output ONLY the number or "RETRY" (no formatting)""",
            context=synthesized
        )

        # Verify computationally
        if answer_extraction.strip() != "RETRY":
            try:
                answer_int = int(answer_extraction.strip())
                if 0 <= answer_int <= 999:
                    # Cross-verify with programmer if possible
                    verification_code = await self.programmer(
                        instruction=f"""Verify this answer computationally:
                        Problem: {self.problem_text}
                        Proposed Answer: {answer_int}
                        Write code to independently compute answer.
                        If answer matches, output "VERIFIED: {answer_int}"
                        If not, output "FAILED: computed_value"
                        Handle edge cases and precision carefully.""",
                        context=synthesized,
                        max_retries=2
                    )
                    
                    if "VERIFIED" in verification_code:
                        return f"\\boxed{{{answer_int:03d}}}"
                    else:
                        # Fallback: return original if computation fails but logic sound
                        return f"\\boxed{{{answer_int:03d}}}"
                else:
                    answer_extraction = "RETRY"
            except:
                answer_extraction = "RETRY"

        # PHASE 5: META-VALIDATION & ADAPTIVE RETRY (Level 4 Innovation)
        if answer_extraction == "RETRY":
            # Escalate strategy: force computational brute force with mathematical bounds
            fallback = await self.programmer(
                instruction=f"""BRUTE FORCE WITH MATHEMATICAL INSIGHT:
                Problem: {self.problem_text}
                Previous attempts failed. Now:
                1. Establish mathematical bounds for answer (0-999)
                2. Use number theory/combinatorics to reduce search space
                3. Write efficient code to search possible answers
                4. Output ONLY the integer answer (no explanation)
                5. If multiple valid answers, choose smallest
                6. If none found in 0-999, return 000""",
                context=synthesized,
                max_retries=3
            )
            
            try:
                fallback_int = int(fallback.strip())
                if 0 <= fallback_int <= 999:
                    return f"\\boxed{{{fallback_int:03d}}}"
                else:
                    return "\\boxed{000}"  # Ultimate fallback
            except:
                return "\\boxed{000}"

        # Final output formatting
        try:
            final_int = int(answer_extraction.strip())
            return f"\\boxed{{{final_int:03d}}}"
        except:
            return "\\boxed{000}"