# Workflow ID: limr_72_0
# Benchmark: limr
# Data Indices: [344, 17]

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

        # === PHASE 1: DEEP CLASSIFICATION & DECOMPOSITION ===
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this mathematical problem. Address:
            1. Primary domain (combinatorics, geometry, number theory, algebra, optimization, etc.)
            2. Solution archetype (recursive, symmetry-based, generating function, modular, coordinate geometry, etc.)
            3. Key constraints and boundary conditions
            4. Expected answer format and range (must be integer 000-999)
            5. Potential pitfalls or non-obvious transformations required
            6. List all given numerical values and their semantic roles
            Output in structured markdown with clear section headers.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction=f"""Given this classification:
            {classification}
            
            Decompose the problem into minimal, ordered subproblems. For each subproblem:
            - Describe what must be solved
            - Justify why it's necessary
            - Specify mathematical tools required
            - List dependencies (which subproblems must be solved first)
            Ensure dependencies reflect causal/logical order, not just sequence.""",
            context=classification
        )

        # === PHASE 2: PARALLEL SOLUTION PATH GENERATION ===
        solution_approaches = [
            "algebraic_formalism",
            "combinatorial_enumeration",
            "geometric_transformation",
            "number_theoretic_reduction"
        ]

        async def generate_approach(approach_type):
            return await self.generate(
                instruction=f"""Develop a complete solution using {approach_type} approach. Steps:
                1. Restate problem in terms suitable for this approach
                2. Show all mathematical transformations
                3. Derive intermediate results with justification
                4. Arrive at final answer (integer 000-999)
                5. Flag any assumptions or leaps
                Base reasoning on this classification: {classification[:1000]}""",
                context=""
            )

        parallel_solutions = await asyncio.gather(
            *[generate_approach(approach) for approach in solution_approaches[:3]]  # Limit to 3 for efficiency
        )

        # === PHASE 3: CRITIQUE & REVISION ===
        async def critique_solution(solution_text):
            return await self.revise(
                instruction="""Critically analyze this solution:
                - Identify logical gaps or unjustified steps
                - Check computational accuracy
                - Verify constraint satisfaction
                - Assess alignment with problem classification
                - Propose specific fixes or alternatives
                Output must be brutally honest — no politeness, only precision.""",
                context=solution_text
            )

        revised_solutions = await asyncio.gather(
            *[critique_solution(sol) for sol in parallel_solutions]
        )

        # === PHASE 4: SYNTHESIS & ENSEMBLE ===
        final_synthesis = await self.ensemble(
            instruction="""Synthesize these revised solutions into one authoritative answer:
            1. Extract correct elements from each
            2. Resolve contradictions with mathematical justification
            3. Fill remaining gaps using strongest available reasoning
            4. Present final answer as integer between 000-999
            5. Include confidence rating (1-5) based on: internal consistency, cross-approach agreement, edge case validation
            If confidence < 4, explicitly state what's uncertain and propose verification strategy.""",
            contexts_list=revised_solutions
        )

        # === PHASE 5: COMPUTATIONAL VERIFICATION ===
        # Extract final answer for validation
        answer_match = re.search(r'\b([0-9]{3})\b', final_synthesis)
        extracted_answer = answer_match.group(1) if answer_match else "000"

        code_verification = await self.programmer(
            instruction=f"""Implement exact mathematical procedure from this synthesis:
            {final_synthesis[:1500]}
            
            Requirements:
            - Compute final answer independently
            - Validate against constraints from classification
            - If multiple answers possible, return the one consistent with highest-confidence solution
            - Output ONLY the 3-digit integer, nothing else
            - If computation fails, return 000""",
            context=final_synthesis,
            max_retries=2
        )

        # === PHASE 6: CONFIDENCE-BASED REFINEMENT ===
        if "confidence" in final_synthesis.lower() and "3" in final_synthesis or "2" in final_synthesis or "1" in final_synthesis:
            # Low confidence — trigger fallback: brute-force for small cases or alternative decomposition
            fallback = await self.generate(
                instruction=f"""Problem solution has low confidence. Reclassify from first principles:
                - Ignore previous classification
                - Consider alternative domains (e.g., if was combinatorics, try geometry)
                - Propose radically different approach
                - Derive answer independently
                Problem: {self.problem_text[:500]}""",
                context=""
            )
            
            fallback_answer = await self.programmer(
                instruction=f"""Implement this fallback approach exactly:
                {fallback[:1000]}
                Return only 3-digit integer.""",
                context=fallback,
                max_retries=1
            )
            return fallback_answer

        # Final output — ensure 3-digit format
        verified_answer = re.search(r'\b([0-9]{3})\b', code_verification)
        return verified_answer.group(1) if verified_answer else extracted_answer