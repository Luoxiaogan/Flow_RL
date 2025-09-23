# Workflow ID: limr_49_0
# Benchmark: limr
# Data Indices: [112, 184]

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

        # PHASE 1: PROBLEM DECOMPOSITION & CLASSIFICATION
        decomposition_instruction = """
        Systematically decompose this mathematical problem into atomic subproblems. For each subproblem:
        1. Identify its mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
        2. Specify required techniques (proof, calculation, optimization, etc.)
        3. List dependencies on other subproblems
        4. Estimate computational complexity (low/medium/high)
        5. Flag if it requires external theorems or non-trivial insights
        Return structured decomposition with clear IDs and dependency chains.
        """
        decomposition = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION EXPLORATION
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            
            # Generate multiple solution approaches
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Approach 1 for {sub_id}: Solve using direct computation and algebraic manipulation. Show all steps. Verify dimensional consistency.""",
                    context=description
                ),
                self.generate(
                    instruction=f"""Approach 2 for {sub_id}: Solve using mathematical induction or proof by contradiction if applicable. If not, use combinatorial reasoning.""",
                    context=description
                ),
                self.generate(
                    instruction=f"""Approach 3 for {sub_id}: Transform problem into coordinate geometry or complex numbers if possible. Otherwise, use generating functions or recursive relations.""",
                    context=description
                )
            )
            
            # Refine each approach with validation
            refined_approaches = []
            for i, approach in enumerate(approaches):
                refined = await self.revise(
                    instruction=f"""
                    CRITICALLY REVISE Approach {i+1} for {sub_id}:
                    - Check for algebraic errors
                    - Verify boundary conditions
                    - Ensure all constraints are satisfied
                    - Flag any unproven assumptions
                    - If computational, prepare for code generation
                    Output only the corrected, rigorous solution.
                    """,
                    context=approach
                )
                refined_approaches.append(refined)
            
            # Ensemble best approaches
            if len(refined_approaches) > 1:
                ensembled = await self.ensemble(
                    instruction=f"""
                    SYNTHESIZE solutions for {sub_id}:
                    - Resolve contradictions by tracing to root assumptions
                    - Prefer solutions with explicit verification steps
                    - Combine complementary insights
                    - Output single coherent solution with confidence score (0-100%)
                    """,
                    contexts_list=refined_approaches
                )
            else:
                ensembled = refined_approaches[0]
            
            return {"id": sub_id, "solution": ensembled}

        # Solve all subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in decomposition]
        )

        # PHASE 3: GLOBAL SYNTHESIS & VERIFICATION
        # Build context from all subproblem solutions
        full_context = "\n\n".join([
            f"SUBPROBLEM {sol['id']}:\n{sol['solution']}"
            for sol in subproblem_solutions
        ])

        # Generate final answer with multiple verification layers
        final_attempts = await asyncio.gather(
            self.generate(
                instruction="""
                FINAL SOLUTION ATTEMPT 1:
                Synthesize all subproblem solutions into complete answer.
                - Cross-verify dependencies
                - Ensure integer answer between 000-999
                - Format as: "ANSWER: XXX" where XXX is the integer
                - Include brief justification
                """,
                context=full_context
            ),
            self.generate(
                instruction="""
                FINAL SOLUTION ATTEMPT 2:
                Alternative synthesis focusing on computational verification.
                - Convert key steps to pseudocode
                - Identify critical calculations
                - Output answer as "ANSWER: XXX" with error bounds if any
                """,
                context=full_context
            )
        )

        # Ensemble final answers
        final_answer = await self.ensemble(
            instruction="""
            SELECT FINAL ANSWER:
            - Compare both attempts
            - Prefer solutions with explicit numerical verification
            - If disagreement, trace to specific subproblem and re-evaluate
            - Output ONLY the integer answer in format "ANSWER: XXX"
            - Confidence must be >90% or trigger revision
            """,
            contexts_list=final_attempts
        )

        # FINAL VERIFICATION & EXTRACTION
        verified_answer = await self.revise(
            instruction="""
            FINAL VERIFICATION:
            - Extract integer from "ANSWER: XXX" format
            - Validate it's between 000-999
            - If not, return 000 as fallback
            - Output ONLY the 3-digit integer with no text
            """,
            context=final_answer
        )

        return verified_answer.strip()