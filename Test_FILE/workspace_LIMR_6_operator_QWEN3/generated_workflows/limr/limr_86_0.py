# Workflow ID: limr_86_0
# Benchmark: limr
# Data Indices: [52, 139]

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

        # PHASE 1: Hierarchical Problem Decomposition
        decomposition_instruction = """
        Systematically decompose this mathematical problem into the smallest possible set of independent subproblems.
        Each subproblem should be solvable using at most two mathematical techniques (e.g., algebra + geometry, number theory + combinatorics).
        For each subproblem:
        - Clearly state what needs to be computed or proven
        - Identify required inputs and expected outputs
        - Specify mathematical domains involved (algebra, geometry, number theory, etc.)
        - List dependencies on other subproblems
        - Flag any subproblems that seem ambiguous or require additional assumptions
        Output must be in machine-readable format for downstream processing.
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: Parallel Multi-Perspective Solution Generation
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            
            # Generate 3 different solution approaches in parallel
            approaches = [
                f"Approach 1 (Algebraic): Solve '{sp_desc}' using algebraic manipulation, equation solving, and symbolic reasoning.",
                f"Approach 2 (Geometric/Visual): Solve '{sp_desc}' using geometric interpretation, coordinate systems, or visual/spatial reasoning.",
                f"Approach 3 (Computational/Algorithmic): Solve '{sp_desc}' using algorithmic thinking, case analysis, or computational verification."
            ]
            
            solutions = await asyncio.gather(*[
                self.generate(
                    instruction=f"""{approach}
                    - Show all intermediate steps
                    - Justify each mathematical operation
                    - State any assumptions explicitly
                    - Verify consistency with problem constraints
                    - If stuck, explain why and what's missing""",
                    context=""
                ) for approach in approaches
            ])
            
            # Ensemble select best solution for this subproblem
            best_solution = await self.ensemble(
                instruction=f"""Select the most mathematically rigorous and complete solution for subproblem {sp_id}: '{sp_desc}'
                Criteria:
                1. Mathematical correctness (highest priority)
                2. Completeness of reasoning
                3. Clarity of explanation
                4. Alignment with problem constraints
                5. Computational verifiability
                If no solution is fully correct, synthesize a new solution combining the strongest elements from each.""",
                contexts_list=solutions
            )
            
            return {
                'id': sp_id,
                'description': sp_desc,
                'solution': best_solution,
                'approaches': solutions
            }

        # Solve all subproblems in parallel
        subproblem_results = await asyncio.gather(*[
            solve_subproblem(sp) for sp in subproblems
        ])

        # PHASE 3: Adversarial Validation and Refinement
        validated_results = []
        for result in subproblem_results:
            # Attempt to break the solution
            critique = await self.generate(
                instruction=f"""Adversarially critique this solution:
                Subproblem: {result['description']}
                Proposed Solution: {result['solution']}
                
                Try to find flaws, edge cases, or hidden assumptions. Specifically:
                - Are there unstated constraints being violated?
                - Are there alternative interpretations of the problem?
                - Does the solution handle boundary conditions?
                - Are there calculation errors or logical gaps?
                - Would this solution fail for specific input values?
                If no flaws found, state "SOLUTION VALIDATED".""",
                context=result['solution']
            )
            
            # Revise if flaws found
            if "SOLUTION VALIDATED" not in critique.upper():
                revised = await self.revise(
                    instruction=f"""Fix all identified flaws in this solution:
                    Original Solution: {result['solution']}
                    Critique: {critique}
                    
                    Requirements:
                    - Address every point raised in the critique
                    - Maintain mathematical rigor
                    - Show corrected calculations explicitly
                    - Verify the revised solution against original problem constraints""",
                    context=result['solution']
                )
                result['solution'] = revised
                result['validation_status'] = "REVISED"
            else:
                result['validation_status'] = "VALIDATED"
            
            validated_results.append(result)

        # PHASE 4: Global Synthesis and Final Answer Extraction
        synthesis_context = "\n\n".join([
            f"Subproblem {r['id']}: {r['description']}\nSolution: {r['solution']}\nStatus: {r['validation_status']}"
            for r in validated_results
        ])
        
        final_synthesis = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into a complete, coherent answer to the original problem.
            Context: {synthesis_context}
            
            Requirements:
            - Show how subproblem solutions combine to answer the original question
            - Verify global consistency (no contradictions between subproblems)
            - Handle any remaining edge cases or special conditions
            - State the final answer clearly and unambiguously
            - The final answer must be an integer between 000 and 999 as required by LIMR format
            - If the answer is not yet in integer form, perform final simplification""",
            context=synthesis_context
        )

        # PHASE 5: Computational Verification and Answer Normalization
        final_answer = await self.programmer(
            instruction=f"""Extract and verify the final numerical answer from this synthesis:
            {final_synthesis}
            
            Steps:
            1. Parse the final answer from the text (should be an integer 000-999)
            2. If answer is expressed as formula, compute exact value
            3. Verify answer satisfies all original problem constraints
            4. Format as 3-digit string with leading zeros if needed (e.g., 42 → "042")
            5. Return ONLY the 3-digit string, nothing else""",
            context=final_synthesis
        )

        return final_answer