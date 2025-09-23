# Workflow ID: limr_116_0
# Benchmark: limr
# Data Indices: [10, 311]

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
        
        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Perform deep semantic classification of this mathematical problem:
            1. Identify the primary mathematical domain (algebra, geometry, combinatorics, number theory, etc.)
            2. Determine the core reasoning type: proof-based, computational, optimization, case analysis, etc.
            3. List required mathematical tools: trigonometric identities, modular arithmetic, induction, coordinate geometry, etc.
            4. Flag potential pitfalls: hidden constraints, edge cases, common misconceptions.
            5. Suggest 2-3 high-level solution strategies with their trade-offs.
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction=f"""Based on this classification:
            {classification}
            
            Decompose the problem into minimal, logically independent subproblems.
            For each subproblem:
            - Clearly state what needs to be solved
            - Specify mathematical tools required
            - List dependencies (other subproblems that must be solved first)
            - Flag if it requires computational verification
            Prioritize decomposition that exposes parallelizable components.""",
            context=classification
        )

        # PHASE 3: PARALLEL SUBPROBLEM EXPLORATION
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            
            # Generate multiple solution approaches
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Subproblem {sp_id}: {sp_desc}
                    Approach 1: Use the most direct mathematical method. Show all steps rigorously.
                    Include: assumptions, theorems used, and verification steps.""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Subproblem {sp_id}: {sp_desc}
                    Approach 2: Use an alternative mathematical perspective (e.g., if algebraic, try geometric).
                    Focus on creative insight and non-obvious transformations.""",
                    context=classification
                )
            )
            
            # Ensemble best approach
            best_approach = await self.ensemble(
                instruction=f"""Evaluate these approaches for Subproblem {sp_id}:
                Criteria:
                1. Logical completeness (no gaps)
                2. Computational feasibility
                3. Elegance and minimality
                4. Alignment with problem constraints
                Select the single best approach and justify your choice.""",
                contexts_list=approaches
            )
            
            # Revise for rigor and clarity
            refined = await self.revise(
                instruction="""Enhance this solution:
                - Fill any logical gaps
                - Add missing justifications
                - Standardize mathematical notation
                - Verify all intermediate steps
                - Highlight key insights""",
                context=best_approach
            )
            
            # Check if computational verification is needed
            if "computational" in subproblem['description'].lower() or "calculate" in subproblem['description'].lower():
                # Extract computable expression
                computable = await self.generate(
                    instruction="""Extract the precise mathematical expression or algorithm that needs computation.
                    Format it as a standalone Python-compatible expression or algorithm description.
                    If no explicit computation is needed, return "NONE".""",
                    context=refined
                )
                
                if "NONE" not in computable:
                    computation = await self.programmer(
                        instruction=f"""Compute this mathematical expression with exact precision:
                        {computable}
                        Return only the numerical result. Handle edge cases and precision issues.""",
                        context=refined
                    )
                    # Integrate computation into solution
                    refined = await self.revise(
                        instruction=f"""Integrate this computational result: {computation}
                        Update the solution to include this verified result.
                        Ensure consistency with the rest of the reasoning.""",
                        context=refined
                    )
            
            return {"id": sp_id, "solution": refined}

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in decomposition]
        )
        
        # Create solution map for dependency resolution
        solution_map = {sol['id']: sol['solution'] for sol in subproblem_solutions}

        # PHASE 4: SOLUTION SYNTHESIS
        synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solution_map.items()])
        
        synthesized = await self.generate(
            instruction=f"""Synthesize a complete, coherent solution from these subproblem solutions:
            {synthesis_context}
            
            Requirements:
            - Maintain logical flow between subproblems
            - Resolve any interdependencies
            - Ensure global consistency (e.g., same variable has same value everywhere)
            - Present as a single, polished mathematical proof/solution
            - Highlight the final answer prominently""",
            context=synthesis_context
        )

        # PHASE 5: ADVERSARIAL VALIDATION & REFINEMENT
        validation = await self.generate(
            instruction="""Critically evaluate this complete solution:
            1. Are there any logical inconsistencies?
            2. Are all assumptions justified?
            3. Are edge cases properly handled?
            4. Is the final answer correctly derived?
            5. What is the confidence level (high/medium/low)?
            If confidence is not high, suggest specific improvements.""",
            context=synthesized
        )

        if "low" in validation.lower() or "medium" in validation.lower():
            synthesized = await self.revise(
                instruction=f"""Address these validation concerns:
                {validation}
                
                Revise the solution to fix all identified issues.
                If necessary, reconsider fundamental assumptions.
                Prioritize correctness over elegance.""",
                context=synthesized
            )

        # PHASE 6: FINAL ANSWER EXTRACTION & FORMATTING
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer from this solution.
            Rules:
            - If multiple answers, list them comma-separated in ascending order
            - Must be integer(s) between 000 and 999
            - Remove all units, explanations, and formatting
            - If no valid answer, return "000"
            - If answer is a set, sort numerically
            Return ONLY the answer in the required format.""",
            context=synthesized
        )

        # Clean and validate format
        # Remove any non-digit or non-comma characters
        cleaned = re.sub(r'[^0-9,]', '', final_answer)
        # Ensure it's in correct format
        parts = cleaned.split(',')
        # Validate each part is 0-999
        validated_parts = []
        for p in parts:
            if p.isdigit():
                num = int(p)
                if 0 <= num <= 999:
                    validated_parts.append(f"{num:03d}" if len(p) < 3 else p)
        
        if not validated_parts:
            return "000"
        
        # Return sorted, comma-separated
        return ",".join(sorted(validated_parts))