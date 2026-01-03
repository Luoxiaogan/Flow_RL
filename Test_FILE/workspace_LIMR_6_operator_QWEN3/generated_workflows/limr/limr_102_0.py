# Workflow ID: limr_102_0
# Benchmark: limr
# Data Indices: [42, 308]

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
        import json

        # --- PHASE 1: STRUCTURAL DECOMPOSITION & CONSTRAINT EXTRACTION ---
        decomposition_task = self.decompose(
            instruction="""Perform deep semantic decomposition of the problem. For each component:
            1. Identify mathematical domain (algebra, number theory, geometry, combinatorics, etc.)
            2. Extract key variables, constraints, and invariants
            3. Suggest applicable theorems, identities, or transformations
            4. Flag any symmetries, periodicities, or bounding conditions
            5. Propose potential solution pathways (e.g., 'modular arithmetic', 'coordinate geometry', 'generating functions')
            Return as structured list of subproblems with dependencies.""",
            context=""
        )

        constraint_extraction_task = self.generate(
            instruction="""Extract all explicit and implicit constraints:
            - Variable domains (e.g., 'n is positive integer', 'z is complex with |z|=√2')
            - Boundary conditions (e.g., 'n > 8', 'answer between 000-999')
            - Hidden assumptions (e.g., 'real numbers unless specified', 'distinct elements')
            - Answer format requirements (e.g., 'integer', 'simplified fraction')
            Format as bullet-point list with categorization.""",
            context=""
        )

        decomposition, constraints = await asyncio.gather(decomposition_task, constraint_extraction_task)

        # --- PHASE 2: PARALLEL STRATEGY THREADS ---
        async def strategy_thread(strategy_type, decomposition_insight, constraints_summary):
            try:
                # Generate initial approach
                approach = await self.generate(
                    instruction=f"""Develop a {strategy_type.upper()} solution strategy:
                    Problem decomposition insight: {decomposition_insight}
                    Key constraints: {constraints_summary}
                    
                    Steps:
                    1. Propose initial transformations or substitutions
                    2. Identify critical lemmas or theorems to apply
                    3. Outline computational or proof steps
                    4. Anticipate potential pitfalls or edge cases
                    Be detailed and mathematically precise.""",
                    context=""
                )

                # Refine and add rigor
                refined_approach = await self.revise(
                    instruction="""Enhance mathematical rigor:
                    - Fill logical gaps
                    - Justify each non-trivial step
                    - Add necessary inequalities, bounds, or modular conditions
                    - Ensure all variables are properly constrained
                    - Format for computational implementation if applicable""",
                    context=approach
                )

                # Execute if computational
                if strategy_type in ["algebraic", "computational", "geometric"]:
                    code_result = await self.programmer(
                        instruction=f"""Implement the mathematical solution from this approach:
                        {refined_approach}
                        
                        Requirements:
                        - Use exact arithmetic (no floats unless unavoidable)
                        - Handle edge cases explicitly
                        - Return final answer as integer between 000-999
                        - Include verification step if possible""",
                        context=refined_approach,
                        max_retries=2
                    )
                    return f"STRATEGY: {strategy_type}\nAPPROACH: {refined_approach}\nRESULT: {code_result}"
                else:
                    # For proof-based or combinatorial, validate logically
                    validation = await self.generate(
                        instruction=f"""Critically validate this proof/argument:
                        {refined_approach}
                        
                        Check:
                        - Logical consistency
                        - Adherence to constraints
                        - No unwarranted assumptions
                        - Conclusion follows from premises
                        Return 'VALID' or detailed critique.""",
                        context=refined_approach
                    )
                    return f"STRATEGY: {strategy_type}\nAPPROACH: {refined_approach}\nVALIDATION: {validation}"
            except Exception as e:
                return f"STRATEGY: {strategy_type}\nERROR: {str(e)}"

        # Launch parallel strategy threads
        strategy_types = ["algebraic", "structural_proof", "geometric_complex", "combinatorial"]
        strategy_tasks = [
            strategy_thread(stype, str(decomposition)[:500], constraints[:500]) 
            for stype in strategy_types
        ]
        strategy_results = await asyncio.gather(*strategy_tasks)

        # --- PHASE 3: CROSS-VALIDATION & ERROR CORRECTION ---
        validated_results = []
        for result in strategy_results:
            if "ERROR" in result:
                validated_results.append(result)
                continue
            
            # Self-validation loop (max 2 iterations)
            current_result = result
            for _ in range(2):
                validation_check = await self.generate(
                    instruction=f"""Critique this solution for mathematical soundness:
                    {current_result}
                    
                    Specifically check:
                    - Computational accuracy (if applicable)
                    - Logical completeness
                    - Constraint satisfaction
                    - Answer format compliance (integer 000-999)
                    Return 'PASSED' or detailed correction instructions.""",
                    context=current_result
                )
                
                if "PASSED" in validation_check.upper():
                    validated_results.append(current_result)
                    break
                else:
                    current_result = await self.revise(
                        instruction=f"""Correct the solution based on this critique:
                        {validation_check}
                        
                        Maintain mathematical rigor and precision.
                        Ensure final answer is an integer between 000-999.""",
                        context=current_result
                    )
            else:
                # If still not passed, append with validation warning
                validated_results.append(f"{current_result}\nVALIDATION_WARNING: Failed final validation")

        # --- PHASE 4: ENSEMBLE SYNTHESIS & FINAL REFINEMENT ---
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution from these parallel strategies:
            - Prioritize solutions that passed validation
            - Prefer computationally verified results over unverified proofs
            - If multiple valid answers, select based on: (1) most constrained, (2) simplest derivation, (3) highest confidence
            - If contradictions, identify root cause and resolve using most rigorous approach
            - Ensure final answer is integer 000-999 with complete justification
            - If no solution is fully valid, return the most promising with explicit caveats""",
            contexts_list=validated_results
        )

        # Final polish for competition format
        competition_ready = await self.revise(
            instruction="""Transform into competition-ready answer:
            - Final answer must be integer between 000-999, boxed as \\boxed{###}
            - All steps must be traceable and justified
            - No approximations or floating point unless proven exact
            - Include brief rationale for key insights
            - Remove redundant explanations, keep only essential logic
            - Format for clarity and elegance""",
            context=final_answer
        )

        return competition_ready