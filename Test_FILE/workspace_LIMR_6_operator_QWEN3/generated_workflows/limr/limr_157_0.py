# Workflow ID: limr_157_0
# Benchmark: limr
# Data Indices: [4, 315]

import asyncio

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

        # PHASE 1: PROBLEM CLASSIFICATION & HIGH-LEVEL DECOMPOSITION
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your output must include:
            1. Problem Type: Classify as Geometry, Number Theory, Algebra, Combinatorics, Optimization, or Sequence.
            2. Key Entities: List all variables, constants, functions, and constraints explicitly mentioned.
            3. Solution Strategies: Propose 2-3 viable high-level approaches (e.g., 'polynomial division', 'inclusion-exclusion', 'coordinate geometry').
            4. Complexity Estimate: Rate from 1-5 based on steps required and insight depth.
            5. Ambiguity Check: Flag any ambiguous phrasing or missing constraints.
            Format your response with clear section headers.""",
            context=""
        )

        # PHASE 2: FORMAL DECOMPOSITION INTO SUBPROBLEMS
        try:
            decomposition = await self.decompose(
                instruction="""Decompose this problem into a minimal set of interdependent subproblems. For each subproblem:
                - Assign a unique ID (e.g., SP1, SP2)
                - Provide a precise, self-contained description
                - List prerequisite subproblem IDs (comma-separated, or 'none' if independent)
                - Tag with required skill: [Algebraic, Computational, Logical, Geometric, Combinatorial]
                Prioritize subproblems that can be solved in parallel. Ensure the final subproblem synthesizes all results into the required integer answer (000-999).""",
                context=classification
            )
        except Exception:
            # Fallback: Attempt holistic solution if decomposition fails
            decomposition = [{
                "id": "SP1",
                "description": "Solve the entire problem holistically without decomposition.",
                "dependencies": "none",
                "skill_tag": "Holistic"
            }]

        # PHASE 3: PARALLEL SOLUTION OF INDEPENDENT SUBPROBLEMS
        subproblem_results = {}
        subproblem_ids = [sp["id"] for sp in decomposition]
        
        # Group subproblems by independence for parallel execution
        independent_subproblems = [sp for sp in decomposition if sp["dependencies"] == "none"]
        
        async def solve_subproblem(subproblem):
            sp_id = subproblem["id"]
            sp_desc = subproblem["description"]
            skill_tag = subproblem.get("skill_tag", "General")
            
            # Generate multiple solution attempts in parallel for robustness
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve this subproblem using {skill_tag} reasoning:
                    Subproblem: {sp_desc}
                    Constraints: Must contribute to final integer answer 000-999.
                    Show all steps. If numerical computation needed, flag it explicitly.
                    Verify intermediate results. Box final sub-result.""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Solve this subproblem using an ALTERNATIVE {skill_tag} approach:
                    Subproblem: {sp_desc}
                    Constraints: Must contribute to final integer answer 000-999.
                    Show all steps. If numerical computation needed, flag it explicitly.
                    Verify intermediate results. Box final sub-result.""",
                    context=classification
                )
            )
            
            # Ensemble best solution for this subproblem
            best_solution = await self.ensemble(
                instruction=f"""Select the most rigorous and correct solution for subproblem {sp_id}:
                - Prefer solutions with explicit verification steps
                - Ensure numerical results are exact (no approximations)
                - Final sub-result must be clearly boxed
                - Resolve contradictions by cross-checking against problem constraints""",
                contexts_list=solution_attempts
            )
            
            # Validate and iteratively refine if needed
            for _ in range(3):  # Max 3 refinement cycles
                validation = await self.generate(
                    instruction=f"""Critically validate this subproblem solution:
                    - Check for logical consistency
                    - Verify arithmetic and algebraic steps
                    - Ensure alignment with original problem constraints
                    - Flag any assumptions not explicitly justified
                    If no errors, respond 'VALID'. Otherwise, list specific errors.""",
                    context=best_solution
                )
                
                if "VALID" in validation.upper() and "ERROR" not in validation.upper():
                    break
                else:
                    best_solution = await self.revise(
                        instruction=f"""Revise this solution to fix the following issues:
                        Validation Feedback: {validation}
                        Maintain all correct elements. Only modify flawed sections.
                        Ensure final sub-result is boxed and exact.""",
                        context=best_solution
                    )
            
            return sp_id, best_solution

        # Solve all independent subproblems in parallel
        if independent_subproblems:
            independent_results = await asyncio.gather(
                *[solve_subproblem(sp) for sp in independent_subproblems]
            )
            for sp_id, result in independent_results:
                subproblem_results[sp_id] = result

        # Handle dependent subproblems sequentially (simplified for brevity; could be parallelized by dependency level)
        dependent_subproblems = [sp for sp in decomposition if sp["dependencies"] != "none"]
        for subproblem in dependent_subproblems:
            # Wait for dependencies (simplified: assume single dependency or all resolved)
            deps = subproblem["dependencies"].split(",") if subproblem["dependencies"] != "none" else []
            if all(dep.strip() in subproblem_results for dep in deps):
                sp_id, result = await solve_subproblem(subproblem)
                subproblem_results[sp_id] = result

        # PHASE 4: SYNTHESIZE FINAL ANSWER
        all_results_context = "\n\n".join([f"Subproblem {sp_id}: {result}" for sp_id, result in subproblem_results.items()])
        
        final_synthesis = await self.generate(
            instruction=f"""Synthesize all subproblem results into a single final answer:
            - The answer must be an integer between 000 and 999
            - Cross-verify consistency across all subproblem results
            - If contradictions exist, resolve them by re-examining the most uncertain subproblem
            - Present the final answer in a box: \\boxed{{answer}}
            - Include a one-sentence justification linking back to the original problem""",
            context=all_results_context
        )

        # FINAL VALIDATION & FORMATTING
        final_answer = await self.ensemble(
            instruction="""Extract and verify the final integer answer:
            - Must be exactly three digits (000-999)
            - Must be boxed as \\boxed{{answer}}
            - If multiple answers exist, select the one most consistent with all subproblem results
            - If no valid answer, return \\boxed{{000}} as fallback""",
            contexts_list=[final_synthesis, all_results_context]
        )

        # Ensure output format compliance
        match = re.search(r'\\boxed\{(\d{3})\}', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any 3-digit number or return 000
            numbers = re.findall(r'\b\d{3}\b', final_answer)
            return numbers[0] if numbers else "000"