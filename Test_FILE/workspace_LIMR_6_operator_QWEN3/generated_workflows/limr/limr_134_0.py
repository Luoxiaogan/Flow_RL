# Workflow ID: limr_134_0
# Benchmark: limr
# Data Indices: [325, 235]

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

        # PHASE 1: Problem Taxonomy & Structural Decomposition
        problem_classification = await self.generate(
            instruction="""Perform deep problem classification and decomposition:
            1. Identify primary mathematical domain (geometry, number theory, combinatorics, algebra, optimization, sequences)
            2. Detect secondary domains or hybrid elements
            3. Extract all numerical constraints, boundary conditions, and implicit assumptions
            4. Classify required answer type (must be integer 000-999)
            5. Propose initial decomposition strategy
            6. Flag any ambiguous terminology requiring disambiguation
            Output structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: Hierarchical Decomposition
        decomposition_plan = await self.decompose(
            instruction="""Create granular, dependency-aware subproblem decomposition:
            - Break problem into minimal atomic subproblems
            - Each subproblem must be solvable independently given its dependencies
            - Assign unique IDs (e.g., SP1, SP2)
            - Specify dependencies as comma-separated IDs
            - For each subproblem, include: mathematical objective, required techniques, and expected output format
            - Ensure final subproblem produces integer 000-999 answer""",
            context=problem_classification
        )

        # PHASE 3: Parallel Strategy Exploration (Diamond Pattern)
        async def solve_subproblem(subproblem_desc: str, subproblem_id: str) -> dict:
            """Solve one subproblem via three parallel strategies"""
            
            # Strategy A: Analytical Reasoning
            analytical = await self.generate(
                instruction=f"""Solve subproblem {subproblem_id} using pure mathematical reasoning:
                - Show all logical steps and justifications
                - Use appropriate theorems, identities, or principles
                - Maintain exact precision (no approximations)
                - Verify each step before proceeding
                - Final output must be clearly boxed
                Subproblem: {subproblem_desc}""",
                context=problem_classification
            )
            
            # Strategy B: Computational Verification
            computational = await self.programmer(
                instruction=f"""Implement precise computational solution for subproblem {subproblem_id}:
                - Use exact arithmetic (fractions, integers) not floating point
                - Handle edge cases explicitly
                - Validate against analytical approach if possible
                - Output must be single integer or exact fraction convertible to integer
                - Include verification step in code
                Subproblem: {subproblem_desc}""",
                context=analytical  # Use analytical as context for alignment
            )
            
            # Strategy C: Heuristic Validation & Boundary Testing
            heuristic = await self.generate(
                instruction=f"""Validate subproblem {subproblem_id} via heuristic and edge case analysis:
                - Test boundary conditions and extreme cases
                - Apply dimensional analysis or symmetry arguments
                - Check for reasonableness (order of magnitude, parity, divisibility)
                - Identify potential pitfalls or common mistakes
                - Confirm result aligns with analytical and computational outputs
                Subproblem: {subproblem_desc}""",
                context=f"Analytical: {analytical}\n\nComputational: {computational}"
            )
            
            # Critique Layer: Adversarial Revision
            analytical_critique = await self.revise(
                instruction="Adversarial critique: Assume this solution is wrong. Find the flaw in reasoning, calculation, or assumption. Be brutally honest.",
                context=analytical
            )
            computational_critique = await self.revise(
                instruction="Adversarial critique: Assume this code or result is incorrect. Find the bug, precision error, or logical flaw. Check edge cases.",
                context=computational
            )
            heuristic_critique = await self.revise(
                instruction="Adversarial critique: Assume this validation missed something. What edge case or assumption was overlooked?",
                context=heuristic
            )
            
            # Ensemble Synthesis for this subproblem
            subproblem_synthesis = await self.ensemble(
                instruction=f"""Synthesize solutions for subproblem {subproblem_id}:
                - Compare analytical, computational, and heuristic approaches
                - Weight by mathematical rigor and verification strength
                - Resolve conflicts by preferring methods with explicit verification
                - Ensure output is integer 000-999 or convertible to such
                - If uncertainty remains, flag for recursive decomposition
                - Output ONLY the final answer for this subproblem as integer""",
                contexts_list=[
                    f"ANALYTICAL:\n{analytical}\nCRITIQUE:\n{analytical_critique}",
                    f"COMPUTATIONAL:\n{computational}\nCRITIQUE:\n{computational_critique}",
                    f"HEURISTIC:\n{heuristic}\nCRITIQUE:\n{heuristic_critique}"
                ]
            )
            
            return {
                'id': subproblem_id,
                'synthesis': subproblem_synthesis,
                'all_data': {
                    'analytical': analytical,
                    'computational': computational,
                    'heuristic': heuristic,
                    'critiques': {
                        'analytical': analytical_critique,
                        'computational': computational_critique,
                        'heuristic': heuristic_critique
                    }
                }
            }

        # Execute all subproblems in parallel
        subproblem_tasks = []
        for sp in decomposition_plan:
            subproblem_tasks.append(
                solve_subproblem(sp['description'], sp['id'])
            )
        
        subproblem_results = await asyncio.gather(*subproblem_tasks)
        
        # Create result lookup for dependency resolution
        result_map = {res['id']: res['synthesis'] for res in subproblem_results}
        
        # PHASE 4: Final Synthesis & Validation
        # Reconstruct full solution from subproblem results
        final_context = "\n".join([
            f"Subproblem {res['id']}: {res['synthesis']}"
            for res in subproblem_results
        ])
        
        final_answer_draft = await self.generate(
            instruction="""Construct final answer from subproblem results:
            - Combine subproblem outputs according to dependency graph
            - Show final calculation step if needed
            - Ensure answer is integer between 000 and 999
            - If fractional, simplify exactly to integer
            - Box final answer as \boxed{XXX} where XXX is 3-digit integer
            - Include brief justification referencing subproblem results""",
            context=final_context
        )
        
        # Final Adversarial Validation
        final_validation = await self.revise(
            instruction="""Final adversarial validation:
            - Assume final answer is wrong. Find flaw.
            - Verify integer constraint (000-999)
            - Check unit consistency and mathematical soundness
            - Ensure no step was skipped or assumed
            - If error found, correct it and re-output boxed answer""",
            context=final_answer_draft
        )
        
        # Extract final integer answer
        answer_match = re.search(r'\\boxed\{(\d{3})\}', final_validation)
        if answer_match:
            final_answer = answer_match.group(1)
        else:
            # Fallback: extract any 3-digit number
            digits_match = re.search(r'\b(\d{3})\b', final_validation)
            final_answer = digits_match.group(1) if digits_match else "000"
        
        return final_answer