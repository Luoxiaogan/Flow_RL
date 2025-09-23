# Workflow ID: limr_66_0
# Benchmark: limr
# Data Indices: [249, 250]

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

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY IDENTIFICATION
        classification = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Identify mathematical domain(s): algebra, number theory, combinatorics, geometry, etc.
            2. Determine solution type: proof, computation, optimization, enumeration, etc.
            3. List required techniques: induction, modular arithmetic, coordinate geometry, etc.
            4. Flag potential pitfalls: common misconceptions, edge cases, symmetry assumptions.
            5. Estimate complexity: number of steps, depth of reasoning required.
            6. Suggest 2-3 viable solution strategies with pros/cons.
            Format as structured JSON with keys: domain, solution_type, techniques, pitfalls, complexity, strategies.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction=f"""Break problem into minimal solvable subproblems:
            Based on classification: {classification}
            
            Requirements:
            - Each subproblem must be independently verifiable
            - Specify dependencies between subproblems
            - Include computational, logical, and verification subproblems
            - For computational subproblems, specify input/output format
            - For proof subproblems, specify required lemmas or theorems
            
            Return list of subproblems with IDs, descriptions, and dependencies.""",
            context=classification
        )

        # PHASE 3: PARALLEL SUBPROBLEM SOLVING
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            
            # Generate multiple solution approaches in parallel
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve subproblem using ALGEBRAIC approach:
                    Subproblem: {description}
                    Original classification: {classification}
                    Requirements: Show all steps, justify each transformation, verify domain restrictions.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve subproblem using COMPUTATIONAL approach:
                    Subproblem: {description}
                    Original classification: {classification}
                    Requirements: If applicable, write pseudocode or algorithm steps. Consider edge cases and boundary conditions.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve subproblem using PROOF-BASED approach:
                    Subproblem: {description}
                    Original classification: {classification}
                    Requirements: Use formal mathematical reasoning. State assumptions clearly. Consider proof by contradiction or induction if applicable.""",
                    context=""
                )
            )
            
            # Ensemble best solution for this subproblem
            best_solution = await self.ensemble(
                instruction=f"""Select and refine the best solution for subproblem {sub_id}:
                - Must be mathematically rigorous
                - Must handle all edge cases mentioned in classification
                - Prefer solutions with verifiable steps
                - If multiple are correct, synthesize strongest elements
                - Format: Clear step-by-step reasoning ending with boxed answer if applicable""",
                contexts_list=solution_attempts
            )
            
            # Validate solution
            validated_solution = await self.revise(
                instruction=f"""Adversarial validation of solution for subproblem {sub_id}:
                Assume this solution is WRONG. Find the flaw.
                - Check every mathematical step
                - Verify against edge cases from classification
                - Test with extreme values or counterexamples
                - If no flaw found, strengthen with additional verification method
                - If flaw found, fix it and re-verify""",
                context=best_solution
            )
            
            return {
                'id': sub_id,
                'description': description,
                'solution': validated_solution
            }

        # Solve all independent subproblems in parallel
        solved_subproblems = []
        subproblem_map = {sp['id']: sp for sp in decomposition}
        
        # Handle dependencies by solving in topological order
        solved_ids = set()
        remaining_subproblems = decomposition.copy()
        
        while remaining_subproblems:
            # Find subproblems whose dependencies are satisfied
            ready_subproblems = [
                sp for sp in remaining_subproblems 
                if all(dep.strip() in solved_ids for dep in sp.get('dependencies', '').split(',') if dep.strip())
            ]
            
            if not ready_subproblems:
                # Circular dependency or missing subproblem - break
                break
                
            # Solve ready subproblems in parallel
            solutions = await asyncio.gather(*[
                solve_subproblem(sp) for sp in ready_subproblems
            ])
            
            # Update solved subproblems
            solved_subproblems.extend(solutions)
            solved_ids.update(sp['id'] for sp in ready_subproblems)
            remaining_subproblems = [sp for sp in remaining_subproblems if sp not in ready_subproblems]
        
        # PHASE 4: SYNTHESIZE FINAL SOLUTION
        synthesis_context = "\n\n".join([
            f"Subproblem {sp['id']}: {sp['description']}\nSolution: {sp['solution']}"
            for sp in solved_subproblems
        ])
        
        final_solution = await self.generate(
            instruction=f"""Synthesize complete solution from subproblem solutions:
            Classification: {classification}
            Subproblem Solutions: {synthesis_context}
            
            Requirements:
            - Integrate all subproblem solutions into coherent whole
            - Maintain mathematical rigor throughout
            - Highlight connections between subproblems
            - Final answer must be integer between 000-999
            - Box final answer as \\boxed{{answer}}""",
            context=synthesis_context
        )
        
        # PHASE 5: FINAL VALIDATION & ANSWER EXTRACTION
        verified_solution = await self.revise(
            instruction="""Final verification:
            - Ensure answer is integer between 000-999
            - Verify all steps are logically sound
            - Check for calculation errors
            - Confirm answer satisfies original problem constraints
            - If any issue found, fix it immediately""",
            context=final_solution
        )
        
        # Extract final answer
        answer = await self.summarize(
            instruction="""Extract final integer answer:
            - Find the integer between 000-999 that is the final answer
            - If multiple integers, select the one that solves the original problem
            - If no valid answer found, return 'ERROR'
            - Return ONLY the 3-digit integer (with leading zeros if needed)""",
            context=verified_solution
        )
        
        # Clean answer format
        answer_clean = re.sub(r'\D', '', answer)
        if len(answer_clean) == 1:
            answer_clean = '00' + answer_clean
        elif len(answer_clean) == 2:
            answer_clean = '0' + answer_clean
        elif len(answer_clean) > 3:
            answer_clean = answer_clean[-3:]
        
        return answer_clean[:3] if answer_clean.isdigit() and len(answer_clean) >= 3 else "000"