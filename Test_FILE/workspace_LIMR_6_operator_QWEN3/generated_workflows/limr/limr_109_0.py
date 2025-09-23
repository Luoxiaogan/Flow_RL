# Workflow ID: limr_109_0
# Benchmark: limr
# Data Indices: [285, 177]

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

        # STEP 1: META-COGNITIVE CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategy mapping:
            1. Identify the primary mathematical domain (geometry, number theory, algebra, combinatorics, sequences, etc.)
            2. List all mathematical objects, quantities, and relationships mentioned
            3. Infer the type of answer required (length, sum, count, probability, etc.)
            4. Propose 2-3 distinct solution strategies with their theoretical basis
            5. Flag any potential pitfalls or non-obvious insights required
            6. Estimate the number of reasoning steps needed
            Format as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, logically independent subproblems:
            - Each subproblem should be solvable in isolation if dependencies are met
            - Specify dependencies using subproblem IDs (e.g., "2,3" means depends on subproblems 2 and 3)
            - Prioritize subproblems that unlock multiple downstream steps
            - Include at least one computational subproblem suitable for code verification
            - Ensure the final subproblem produces the required integer answer (000-999)
            Return as list of dictionaries with 'id', 'description', 'dependencies'.""",
            context=classification
        )

        # STEP 3: PARALLEL SOLUTION ATTEMPTS (DIAMOND PATTERN)
        # Generate 3 distinct solution approaches based on classification
        approach_instructions = [
            """Develop a solution using the first strategy proposed in classification:
            - Follow the mathematical formalism appropriate to the domain
            - Show all intermediate steps with clear justifications
            - Highlight any non-trivial insights or transformations
            - Structure as a coherent mathematical argument""",
            """Develop a solution using an alternative strategy (different from first):
            - Prefer computational or algorithmic approaches if applicable
            - Use coordinate geometry, brute force, or generating functions if suitable
            - Include explicit calculations and variable tracking
            - Structure as a step-by-step procedure""",
            """Develop a solution focusing on pattern recognition and invariants:
            - Look for symmetries, recursive structures, or conserved quantities
            - Use mathematical induction or telescoping if applicable
            - Emphasize conceptual insights over computation
            - Structure as a proof or derivation"""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in approach_instructions]
        )

        # STEP 4: ADVERSARIAL VALIDATION & REFINEMENT
        validated_solutions = []
        for i, attempt in enumerate(solution_attempts):
            # First validation: logical consistency
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution attempt:
                - Check for logical gaps or unjustified assumptions
                - Verify mathematical correctness of each step
                - Identify any calculation errors or misapplications of theorems
                - Assess alignment with problem constraints
                - If errors found, suggest specific corrections
                Solution attempt {i+1}: {attempt}""",
                context=attempt
            )
            
            # Revise if validation finds issues
            if "error" in validation.lower() or "incorrect" in validation.lower() or "gap" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Fix all identified issues while preserving correct elements:
                    Validation feedback: {validation}
                    - Maintain the original approach's core strategy
                    - Correct mathematical errors with detailed working
                    - Fill logical gaps with rigorous justification
                    - Ensure all steps are traceable and verifiable""",
                    context=attempt
                )
                validated_solutions.append(revised)
            else:
                validated_solutions.append(attempt)

        # STEP 5: STRATEGIC SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts:
            - Select the most mathematically rigorous and complete solution
            - Incorporate any superior insights or calculations from other attempts
            - Ensure the final solution is self-contained and logically watertight
            - The answer must be an integer between 000 and 999
            - Format the final answer as: \\boxed{XXX} where XXX is the 3-digit integer
            - If multiple answers conflict, perform a tie-breaker analysis using first principles""",
            contexts_list=validated_solutions
        )

        # STEP 6: COMPUTATIONAL VERIFICATION (WHERE APPLICABLE)
        # Extract any computational subproblems from decomposition for code verification
        computational_checks = []
        for subproblem in decomposition:
            if any(keyword in subproblem['description'].lower() for keyword in ['compute', 'calculate', 'sum', 'value', 'number']):
                try:
                    code_result = await self.programmer(
                        instruction=f"""Implement and execute code to solve this subproblem:
                        Subproblem: {subproblem['description']}
                        - Use exact arithmetic (no floating point approximations)
                        - Return only the final integer result
                        - Handle edge cases and boundary conditions
                        - If recursion is involved, optimize to avoid stack overflow""",
                        context=synthesized_solution,
                        max_retries=2
                    )
                    computational_checks.append(f"Subproblem {subproblem['id']}: {code_result}")
                except Exception:
                    # Skip if programming fails (not all subproblems are computable)
                    continue

        # STEP 7: FINAL VALIDATION & FORMATTING
        final_answer = await self.revise(
            instruction=f"""Perform final validation and format the answer:
            1. Extract the numerical answer from the synthesized solution
            2. Verify it is an integer between 000 and 999
            3. Cross-check with any computational results: {computational_checks}
            4. If discrepancy found, resolve by prioritizing computational verification
            5. Format as exactly \\boxed{{XXX}} where XXX is zero-padded 3-digit integer
            6. If answer is single or double digit, pad with leading zeros (e.g., 5 → 005)
            7. Ensure no explanatory text—only the boxed answer""",
            context=synthesized_solution
        )

        # STEP 8: SAFETY NET - REGEX EXTRACTION (in case formatting fails)
        # Extract the final answer using regex as fallback
        match = re.search(r'\\boxed\{(\d{1,3})\}', final_answer)
        if match:
            answer = match.group(1).zfill(3)  # Zero-pad to 3 digits
            return f"\\boxed{{{answer}}}"
        else:
            # Last resort: return the synthesized solution as-is
            return final_answer