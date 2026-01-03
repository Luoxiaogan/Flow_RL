# Workflow ID: limr_132_0
# Benchmark: limr
# Data Indices: [214, 97]

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
        
        # PHASE 1: Deep Structural Analysis (Problem Genome Extraction)
        problem_genome = await self.generate(
            instruction="""Perform deep mathematical autopsy of the problem:
            1. Identify all mathematical objects (matrices, integers, sequences, sets, functions)
            2. Extract all relationships (equations, inequalities, divisibility, congruences)
            3. Detect hidden symmetries, invariants, or conserved quantities
            4. Hypothesize applicable theorems (Cayley-Hamilton, Chinese Remainder, Pigeonhole, etc.)
            5. List explicit and implicit constraints
            6. Predict solution class (integer, matrix, proof, optimization)
            Format as structured markdown with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Path Generation (Diamond Pattern Fork)
        theorem_path, computational_path, structural_path = await asyncio.gather(
            self.generate(
                instruction=f"""Develop solution using theorem-based reasoning:
                - Apply relevant theorems from problem genome: {problem_genome}
                - Use proof techniques: induction, contradiction, modular arithmetic
                - Show all logical steps with mathematical rigor
                - Verify each step against problem constraints
                - Target exact integer answer between 000-999""",
                context=problem_genome
            ),
            self.generate(
                instruction=f"""Develop algorithmic/computational solution:
                - Translate problem into executable mathematical operations
                - Identify computable subproblems (LCM, GCD, matrix ops, summations)
                - Design step-by-step calculation procedure
                - Anticipate precision requirements and edge cases
                - Target exact integer answer between 000-999""",
                context=problem_genome
            ),
            self.generate(
                instruction=f"""Develop structural/transformational solution:
                - Apply geometric or algebraic transformations (diagonalization, coordinate shifts, substitutions)
                - Exploit symmetries or invariants identified in: {problem_genome}
                - Reformulate problem in simpler equivalent form
                - Use visualization or combinatorial arguments if applicable
                - Target exact integer answer between 000-999""",
                context=problem_genome
            )
        )

        # PHASE 3: Iterative Refinement (Cascade with Feedback)
        refined_paths = []
        for i, path in enumerate([theorem_path, computational_path, structural_path]):
            current = path
            for attempt in range(3):  # Max 3 refinement iterations
                validation = await self.generate(
                    instruction=f"""Critically validate this solution path:
                    - Check logical consistency step by step
                    - Verify all mathematical operations are valid (no division by zero, etc.)
                    - Ensure all problem constraints are satisfied
                    - Identify any unproven assumptions
                    - If errors found, specify exactly where and why""",
                    context=current
                )
                
                if "error" not in validation.lower() and "invalid" not in validation.lower() and "flaw" not in validation.lower():
                    refined_paths.append(current)
                    break
                else:
                    current = await self.revise(
                        instruction=f"""Fix all issues identified in validation:
                        Validation feedback: {validation}
                        - Correct mathematical errors
                        - Fill logical gaps with rigorous proofs
                        - Add missing constraint checks
                        - Maintain exact integer answer requirement""",
                        context=current
                    )
            else:  # If loop completes without break, add last version
                refined_paths.append(current)

        # PHASE 4: Adversarial Synthesis (Ensemble with Cross-Examination)
        synthesized_solution = await self.ensemble(
            instruction="""Perform forensic synthesis of all solution paths:
            1. Compare all three refined solutions point by point
            2. Identify areas of agreement (likely correct) and contradiction (needs resolution)
            3. For contradictions, trace back to first principles and mathematical axioms
            4. Synthesize unified solution that:
               - Preserves correct elements from each path
               - Resolves inconsistencies through rigorous proof
               - Maintains all problem constraints
               - Yields exact integer answer 000-999
            5. If synthesis impossible, select most logically consistent solution and annotate weaknesses
            6. Explicitly handle edge cases: zero answers, impossibility proofs, multiple solutions""",
            contexts_list=refined_paths
        )

        # PHASE 5: Computational Verification (Programmer as Truth Arbiter)
        verification_result = await self.programmer(
            instruction=f"""Generate Python code to verify the proposed solution:
            - Extract proposed answer from: {synthesized_solution}
            - Implement computational verification against ALL original problem constraints
            - Test edge cases and boundary conditions
            - Use exact arithmetic (no floating point)
            - Output 'VERIFIED: <answer>' if correct, 'FAILED: <reason>' if not
            - For matrix problems: use symbolic computation
            - For number theory: use efficient algorithms (sieves, modular arithmetic)""",
            context=synthesized_solution,
            max_retries=3
        )

        # PHASE 6: Adaptive Decomposition (Fallback for Verification Failures)
        if "FAILED" in verification_result:
            # Decompose into atomic subproblems
            subproblems = await self.decompose(
                instruction=f"""Break problem into minimal solvable subproblems:
                - Each subproblem must have clear mathematical objective
                - Specify dependencies between subproblems
                - Ensure subproblems collectively determine final answer
                - Prioritize subproblems that address verification failure: {verification_result}""",
                context=synthesized_solution
            )
            
            # Solve each subproblem independently
            subproblem_solutions = []
            for subproblem in subproblems:
                sub_solution = await self.generate(
                    instruction=f"""Solve this atomic subproblem:
                    {subproblem['description']}
                    - Show complete mathematical reasoning
                    - Verify against subproblem constraints
                    - Output exact numerical result""",
                    context=""
                )
                
                # Verify subproblem solution computationally
                sub_verify = await self.programmer(
                    instruction=f"""Verify this subproblem solution:
                    Subproblem: {subproblem['description']}
                    Solution: {sub_solution}
                    - Generate code to validate subproblem result
                    - Output 'SUB_VERIFIED: <result>' or 'SUB_FAILED: <reason>'""",
                    context=sub_solution,
                    max_retries=2
                )
                
                if "SUB_FAILED" in sub_verify:
                    # Regenerate with error feedback
                    sub_solution = await self.revise(
                        instruction=f"""Fix subproblem solution based on verification failure:
                        Verification: {sub_verify}
                        - Correct mathematical errors
                        - Ensure alignment with subproblem description""",
                        context=sub_solution
                    )
                
                subproblem_solutions.append(f"Subproblem {subproblem['id']}: {sub_solution}")
            
            # Reassemble final solution from verified subproblems
            reassembled = await self.generate(
                instruction=f"""Reconstruct final solution from verified subproblems:
                Subproblem solutions: {'; '.join(subproblem_solutions)}
                - Combine results according to dependency graph
                - Ensure consistency with original problem constraints
                - Output final integer answer 000-999""",
                context=synthesized_solution
            )
            synthesized_solution = reassembled

        # PHASE 7: Final Answer Extraction and Formatting
        final_answer = await self.generate(
            instruction=f"""Extract and format final answer:
            - From solution: {synthesized_solution}
            - Must be integer between 000 and 999
            - Format as three-digit string with leading zeros (e.g., '042' not '42')
            - If multiple valid answers, select smallest positive unless problem specifies otherwise
            - If no solution exists, output '000' only if mathematically proven impossible
            - Output ONLY the three-digit string, nothing else""",
            context=synthesized_solution
        )
        
        # Clean and validate final output
        final_answer = re.sub(r'\D', '', final_answer)  # Remove non-digits
        final_answer = final_answer.zfill(3)[-3:]  # Ensure 3 digits with leading zeros
        
        return final_answer