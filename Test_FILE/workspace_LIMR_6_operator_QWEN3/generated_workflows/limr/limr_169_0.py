# Workflow ID: limr_169_0
# Benchmark: limr
# Data Indices: [30, 339]

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

        # STEP 1: Problem Classification and Structural Decomposition
        classification = await self.generate(
            instruction="""Perform deep problem classification and structural decomposition:
            1. Identify the primary mathematical domain (combinatorics, number theory, algebra, geometry, etc.)
            2. Extract all given quantities, variables, and constraints
            3. Identify what is being asked (final output format, type of answer)
            4. List potential solution strategies (at least 3 distinct mathematical approaches)
            5. Outline any obvious symmetries, invariants, or transformations that could simplify the problem
            Format your response as a structured analysis with clear section headings.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Decompose this problem into minimal, logically dependent subproblems:
            - Each subproblem should be solvable independently given its dependencies
            - Order subproblems by logical dependency (prerequisites first)
            - Include both computational and conceptual steps
            - For each subproblem, specify what mathematical tools or theorems might apply
            Return as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=classification
        )

        # STEP 2: Parallel Strategy Generation (3 distinct approaches)
        strategy_instructions = [
            """Solve the problem using a COMBINATORIAL/PROBABILISTIC approach:
            - Frame the problem in terms of counting, probabilities, or combinatorial identities
            - Use explicit enumeration, generating functions, or probabilistic reasoning
            - Show all counting steps and probability calculations
            - Derive the final answer through combinatorial logic""",
            
            """Solve the problem using an ALGEBRAIC/NUMBER THEORETIC approach:
            - Express relationships as equations, inequalities, or modular constraints
            - Apply algebraic manipulation, factoring, substitution, or number theory theorems
            - Bound variables, test cases, or use divisibility arguments
            - Derive the final answer through algebraic reasoning""",
            
            """Solve the problem using a GEOMETRIC/STRUCTURAL approach:
            - Interpret the problem geometrically or structurally (even if not explicitly geometric)
            - Use symmetry, invariants, transformations, or spatial reasoning
            - Apply geometric theorems, coordinate systems, or vector analysis if applicable
            - Derive the final answer through structural insights"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: Adversarial Validation and Ensemble Synthesis
        # Critique each solution attempt
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically evaluate this solution attempt:
                - Check for logical consistency and mathematical validity
                - Verify all steps follow from previous ones
                - Identify any unjustified assumptions or leaps in reasoning
                - Check computational accuracy (if calculations are shown)
                - Assess whether the final answer matches the problem's requirements
                If errors are found, suggest corrections. If valid, confirm its soundness.""",
                context=attempt
            ) for attempt in strategy_attempts]
        )

        # Synthesize best solution
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the most rigorous and correct solution from the attempts and critiques:
            - Resolve any contradictions between approaches
            - Select the solution with the fewest assumptions and most robust reasoning
            - If multiple solutions agree, use that as confirmation
            - If all solutions have flaws, construct a new solution incorporating the valid parts
            - Ensure the final answer is an integer between 000 and 999
            Output the complete, verified solution with clear reasoning and final answer.""",
            contexts_list=[f"Attempt: {attempt}

Critique: {critique}" 
                      for attempt, critique in zip(strategy_attempts, critiques)]
        )

        # STEP 4: Programmatic Verification
        code_verification = await self.programmer(
            instruction="""Generate Python code to computationally verify the final answer:
            - Extract the key mathematical relationships from the synthesized solution
            - Implement precise calculations (no floating point approximations)
            - If combinatorial, compute exact counts; if algebraic, solve equations programmatically
            - Output should be the integer answer (000-999) as computed
            - Include comments explaining how the code maps to the mathematical reasoning
            - Handle edge cases and validate against problem constraints""",
            context=synthesized_solution,
            max_retries=3
        )

        # STEP 5: Iterative Refinement (if discrepancy exists)
        final_answer = synthesized_solution
        for _ in range(3):  # Max 3 refinement iterations
            # Extract answers from both sources
            symbolic_answer = await self.generate(
                instruction="""Extract ONLY the final integer answer from this solution.
                If multiple numbers are present, select the one that answers the original question.
                Output ONLY the 3-digit integer (with leading zeros if needed), nothing else.""",
                context=final_answer
            )
            
            computational_answer = await self.generate(
                instruction="""Extract ONLY the final integer answer from this code output.
                Parse the result, ignoring any code or explanatory text.
                Output ONLY the 3-digit integer (with leading zeros if needed), nothing else.""",
                context=code_verification
            )

            # Clean and compare
            symbolic_clean = re.sub(r'\D', '', symbolic_answer.strip())[-3:].zfill(3)
            computational_clean = re.sub(r'\D', '', computational_answer.strip())[-3:].zfill(3)

            if symbolic_clean == computational_clean:
                break  # Convergence achieved
            else:
                # Revise based on discrepancy
                final_answer = await self.revise(
                    instruction=f"""Reconcile the discrepancy between symbolic answer ({symbolic_clean}) 
                    and computational answer ({computational_clean}):
                    - Re-examine all assumptions and calculations
                    - Identify which approach (symbolic or computational) likely contains the error
                    - Correct the reasoning and recalculate
                    - Ensure the final answer is consistent across both methods
                    Output the corrected, verified solution.""",
                    context=final_answer
                )
                # Re-run verification if symbolic answer changed
                code_verification = await self.programmer(
                    instruction="""Re-generate verification code based on revised solution:
                    - Update code to reflect corrected reasoning
                    - Recompute the answer
                    - Ensure output matches the revised symbolic answer""",
                    context=final_answer,
                    max_retries=3
                )

        # STEP 6: Final Answer Extraction and Formatting
        final_output = await self.generate(
            instruction="""Extract and format the final answer:
            - From the verified solution, extract ONLY the integer answer
            - Ensure it is between 000 and 999
            - Format as exactly 3 digits with leading zeros if necessary
            - Output NOTHING else — no explanation, no units, just the 3-digit number""",
            context=final_answer
        )

        # Clean final output to ensure compliance
        clean_answer = re.sub(r'\D', '', final_output.strip())[-3:].zfill(3)
        return clean_answer