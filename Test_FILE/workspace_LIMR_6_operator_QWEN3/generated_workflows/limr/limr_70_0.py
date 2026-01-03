# Workflow ID: limr_70_0
# Benchmark: limr
# Data Indices: [204, 297]

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

        # Step 1: Initial problem decomposition into subproblems
        decomposition_instruction = """
        Systematically decompose this mathematical problem into atomic subproblems.
        For each subproblem:
        - Clearly state what needs to be solved or determined
        - Identify any dependencies on other subproblems
        - Specify the mathematical domain (algebra, geometry, number theory, combinatorics, etc.)
        - Note any constraints or boundary conditions
        - Flag if the subproblem requires computational verification
        Structure output as a numbered list with dependency mapping.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Step 2: Parallel exploration from multiple mathematical perspectives
        perspective_instructions = [
            """
            Approach this problem from a NUMBER THEORY perspective:
            - Identify all numerical constraints and divisibility conditions
            - Consider prime factorizations, modular arithmetic, or Diophantine equations
            - Look for patterns in sequences or integer solutions
            - Suggest computational verification points
            """,
            """
            Approach this problem from a COMBINATORIAL/PROBABILISTIC perspective:
            - Identify counting principles, permutations, combinations, or probability distributions
            - Consider generating functions, recursive relations, or inclusion-exclusion
            - Look for symmetries or invariants that simplify counting
            - Suggest computational verification points
            """,
            """
            Approach this problem from a GEOMETRIC/ALGEBRAIC perspective:
            - Identify geometric relationships, coordinate systems, or algebraic structures
            - Consider transformations, ratios, or functional equations
            - Look for similarity, congruence, or optimization principles
            - Suggest computational verification points
            """
        ]

        # Launch parallel explorations
        perspective_analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in perspective_instructions]
        )

        # Step 3: Revise each perspective for rigor and completeness
        revised_analyses = []
        for i, analysis in enumerate(perspective_analyses):
            revise_instruction = f"""
            CRITICALLY REVISE this mathematical analysis (Perspective {i+1}):
            - Fill any logical gaps or missing justifications
            - Explicitly state all assumptions and verify they're valid
            - Add specific calculations or derivations where vague
            - Flag any steps that require computational verification
            - Ensure final answer format complies with 000-999 integer requirement
            - If analysis is fundamentally flawed, explain why and suggest alternative approach
            """
            revised = await self.revise(
                instruction=revise_instruction,
                context=analysis
            )
            revised_analyses.append(revised)

        # Step 4: Ensemble synthesis of revised perspectives
        synthesis_instruction = """
        SYNTHESIZE these mathematical analyses into a unified solution:
        - Identify complementary insights from different perspectives
        - Resolve any contradictions between approaches
        - Construct a step-by-step solution path that leverages the strongest elements
        - Maintain mathematical rigor throughout
        - Explicitly state the final answer as an integer between 000 and 999
        - If multiple valid answers exist, list all and justify each
        """
        synthesized_solution = await self.ensemble(
            instruction=synthesis_instruction,
            contexts_list=revised_analyses
        )

        # Step 5: Computational verification loop (max 2 iterations)
        final_answer = None
        for attempt in range(2):
            try:
                # Extract potential answer for verification
                extract_instruction = """
                From the following solution, extract the FINAL NUMERICAL ANSWER.
                - Return ONLY the integer (no units, no text)
                - If multiple answers, return the smallest valid one
                - If no clear answer, return "UNCLEAR"
                """
                candidate_answer = await self.generate(
                    instruction=extract_instruction,
                    context=synthesized_solution
                )
                
                # Clean and validate answer format
                answer_match = re.search(r'\b\d{1,3}\b', candidate_answer)
                if not answer_match:
                    raise ValueError("No valid integer answer found")
                
                numeric_answer = int(answer_match.group())
                if not (0 <= numeric_answer <= 999):
                    raise ValueError("Answer out of 000-999 range")

                # Verify via computational check if possible
                verify_instruction = f"""
                VERIFY the answer {numeric_answer} for the original problem:
                - Implement a computational check (brute force, simulation, or direct calculation)
                - If verification fails, explain why and suggest correction
                - If verification passes, confirm "VERIFIED"
                - If computational verification is impossible, state "THEORETICAL_ONLY"
                """
                verification = await self.programmer(
                    instruction=verify_instruction,
                    context=synthesized_solution
                )

                if "VERIFIED" in verification or "THEORETICAL_ONLY" in verification:
                    final_answer = f"{numeric_answer:03d}"  # Format as 3-digit string
                    break
                else:
                    # Verification failed - trigger revision
                    revise_instruction = f"""
                    REVISE SOLUTION BASED ON VERIFICATION FAILURE:
                    Verification result: {verification}
                    - Identify the flawed step in reasoning
                    - Correct the mathematical error
                    - Recompute the answer
                    - Ensure final answer is integer 000-999
                    """
                    synthesized_solution = await self.revise(
                        instruction=revise_instruction,
                        context=synthesized_solution
                    )
            except Exception as e:
                # On any error, attempt one revision before giving up
                if attempt == 0:
                    error_revise_instruction = f"""
                    ERROR RECOVERY: Previous attempt failed with error: {str(e)}
                    - Re-examine the entire solution path
                    - Consider alternative mathematical approaches
                    - Focus on edge cases and boundary conditions
                    - Recompute answer with extreme care
                    """
                    synthesized_solution = await self.revise(
                        instruction=error_revise_instruction,
                        context=synthesized_solution
                    )
                else:
                    # Final fallback: extract any number from original synthesis
                    fallback_extract = await self.generate(
                        instruction="Extract ANY plausible integer answer between 000-999",
                        context=synthesized_solution
                    )
                    fallback_match = re.search(r'\b\d{1,3}\b', fallback_extract)
                    if fallback_match:
                        final_answer = f"{int(fallback_match.group()):03d}"
                    else:
                        final_answer = "000"  # Default fallback

        # Step 6: Final formatting and output
        if final_answer is None:
            final_answer = "000"

        return final_answer