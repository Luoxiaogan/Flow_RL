# Workflow ID: limr_129_0
# Benchmark: limr
# Data Indices: [246, 144]

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

        # STEP 1: Problem Classification and Initial Decomposition
        classification = await self.generate(
            instruction="""Perform deep problem classification and initial decomposition:
            1. Identify the primary mathematical domain (combinatorics, number theory, algebra, geometry, etc.)
            2. Detect key constraints, symmetries, or invariants
            3. Note any explicit or implicit bounds (e.g., integer ranges, modular conditions)
            4. Identify what is being asked for (count, value, proof, etc.)
            5. Propose a high-level solution strategy
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: Hierarchical Decomposition into Subproblems
        subproblems = await self.decompose(
            instruction=f"""Based on the classification:
            {classification}

            Decompose this problem into minimal, solvable subproblems. For each:
            - Clearly state what needs to be computed or proven
            - Specify any dependencies on other subproblems
            - Indicate which mathematical tools or theorems are likely required
            Prioritize subproblems that unlock others (foundational steps first).""",
            context=classification
        )

        # STEP 3: Parallel Strategy Exploration for Each Subproblem
        subproblem_solutions = []
        for subproblem in subproblems:
            # Generate multiple approaches for each subproblem
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Subproblem: {subproblem['description']}
                    Strategy 1: Algebraic/Formulaic Approach
                    - Derive exact formulas or equations
                    - Show step-by-step symbolic manipulation
                    - Identify potential pitfalls or edge cases""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Subproblem: {subproblem['description']}
                    Strategy 2: Combinatorial/Enumerative Approach
                    - Break down into cases or use counting principles
                    - Consider symmetries, overcounting, and adjustments
                    - Use small cases to verify pattern""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Subproblem: {subproblem['description']}
                    Strategy 3: Computational/Algorithmic Approach
                    - Outline a step-by-step algorithm or procedure
                    - Identify variables, loops, and termination conditions
                    - Consider efficiency and edge cases""",
                    context=classification
                )
            )
            
            # Synthesize best approach for this subproblem
            best_approach = await self.ensemble(
                instruction=f"""Subproblem: {subproblem['description']}
                Evaluate and synthesize the three approaches below. Select or merge the most rigorous, efficient, and correct solution.
                Criteria:
                1. Mathematical soundness
                2. Completeness (handles all cases)
                3. Clarity of reasoning
                4. Alignment with problem constraints
                Provide the final synthesized solution for this subproblem.""",
                contexts_list=approaches
            )
            
            # Validate and refine the solution
            validated_solution = await self.revise(
                instruction=f"""Subproblem: {subproblem['description']}
                Critically validate the solution below:
                - Check for logical gaps or computational errors
                - Verify against small test cases or known values
                - Ensure all constraints and edge cases are handled
                - Improve clarity and precision of mathematical notation
                If errors are found, correct them and explain the fix.""",
                context=best_approach
            )
            
            subproblem_solutions.append(validated_solution)

        # STEP 4: Integrate Subproblem Solutions into Final Answer
        integrated_solution = await self.generate(
            instruction=f"""Integrate all subproblem solutions into a complete, coherent answer:
            Subproblem Solutions:
            {'---'.join(subproblem_solutions)}

            Steps:
            1. Show how subproblem results combine to answer the original question
            2. Verify consistency across subproblems
            3. Perform final computation or derivation
            4. State the final answer clearly
            Ensure all mathematical steps are explicit and justified.""",
            context="\n\n".join(subproblem_solutions)
        )

        # STEP 5: Computational Verification (if applicable)
        verified_solution = integrated_solution
        try:
            verification_code = await self.generate(
                instruction=f"""Generate Python code to verify the final answer:
                - Implement a brute-force, simulation, or direct computation
                - Handle edge cases and constraints from the original problem
                - Output should be a single integer between 000 and 999
                - Include assertions or checks against the derived answer""",
                context=integrated_solution
            )
            
            code_result = await self.programmer(
                instruction="Execute the verification code and return the result",
                context=verification_code,
                max_retries=3
            )
            
            # Use code result to refine final answer if needed
            verified_solution = await self.ensemble(
                instruction="""Synthesize the symbolic solution and computational verification:
                - If they agree, confirm the answer
                - If they disagree, identify the error and correct the symbolic solution
                - Final answer must be an integer between 000 and 999
                Provide the final, verified answer.""",
                contexts_list=[integrated_solution, code_result]
            )
        except Exception:
            # Fallback: proceed with symbolic solution if code fails
            pass

        # STEP 6: Final Answer Extraction and Formatting
        final_answer = await self.revise(
            instruction="""Extract the final numerical answer:
            - Must be an integer between 000 and 999
            - Format as exactly three digits with leading zeros if necessary (e.g., 042, not 42)
            - If answer is not in this range, re-express or recompute
            - Remove all explanatory text—output ONLY the three-digit number""",
            context=verified_solution
        )

        # Clean and return final answer
        # Extract first 3-digit number from the response
        match = re.search(r'\b\d{3}\b', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return last 3 digits of any number found
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                return numbers[-1][-3:].zfill(3)
            else:
                return "000"  # Ultimate fallback