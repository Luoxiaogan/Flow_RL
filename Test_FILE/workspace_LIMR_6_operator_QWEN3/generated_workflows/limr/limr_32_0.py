# Workflow ID: limr_32_0
# Benchmark: limr
# Data Indices: [122, 148]

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

        # STEP 1: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Adopt an ALGEBRAIC lens: Propose a complete solution strategy focusing on symbolic manipulation, equation transformations, 
            polynomial identities, or functional equations. Identify key algebraic structures, potential substitutions, and theorems to apply. 
            Anticipate computational bottlenecks and suggest simplification tactics. Structure your response as: Strategy Overview, Key Steps, 
            Required Theorems, Potential Pitfalls.""",
            
            """Adopt a COMBINATORIAL/NUMBER THEORETIC lens: Propose a solution strategy emphasizing counting principles, modular arithmetic, 
            divisibility, prime factorization, or combinatorial identities. Look for hidden symmetries, invariants, or recursive structures. 
            Suggest small-case verification and generalization patterns. Structure as: Combinatorial Insight, Step-by-Step Plan, Verification Method, 
            Edge Cases to Consider.""",
            
            """Adopt a COMPUTATIONAL/ALGORITHMIC lens: Propose a strategy centered on writing code to compute or simulate the solution. 
            Identify what to compute (sums, sequences, optimizations), suggest algorithmic approaches (iterative, recursive, dynamic programming), 
            and specify precision requirements. Include fallback methods if direct computation is infeasible. Structure as: Computational Goal, 
            Algorithm Sketch, Code Outline, Validation Plan."""
        ]

        strategy_contexts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # STEP 2: Decompose each strategy into subproblems
        decomposed_strategies = []
        for i, strategy in enumerate(strategy_contexts):
            decomposition = await self.decompose(
                instruction=f"""Break down the following strategy into atomic, verifiable subproblems. Each subproblem must be self-contained, 
                have clear inputs/outputs, and specify dependencies. Prioritize steps that can be computationally verified or symbolically checked. 
                Format each subproblem with: id, description, dependencies (comma-separated ids). Strategy to decompose:
                {strategy}""",
                context=strategy
            )
            decomposed_strategies.append({
                'strategy': strategy,
                'decomposition': decomposition
            })

        # STEP 3: For each decomposition, implement key computational steps and refine
        refined_candidates = []
        for ds in decomposed_strategies:
            strategy = ds['strategy']
            decomposition = ds['decomposition']
            
            # Extract computationally verifiable steps (those mentioning "compute", "calculate", "simulate")
            computational_steps = [
                step for step in decomposition 
                if any(kw in step['description'].lower() for kw in ['compute', 'calculate', 'find', 'determine', 'simulate', 'evaluate'])
            ]
            
            candidate_solutions = []
            for step in computational_steps[:2]:  # Limit to first 2 computable steps to avoid overload
                try:
                    code_result = await self.programmer(
                        instruction=f"""Implement and execute the following mathematical step. Return only the numerical result or computational output. 
                        Step: {step['description']}
                        Context from strategy: {strategy}""",
                        context=strategy,
                        max_retries=2
                    )
                    candidate_solutions.append(f"Step {step['id']}: {code_result}")
                except Exception:
                    continue  # Skip if computation fails

            # Generate initial solution attempt based on strategy
            initial_solution = await self.generate(
                instruction=f"""Using the strategy and any computational results below, derive a complete solution. 
                Show all mathematical steps. Box the final answer. If computational results conflict with symbolic reasoning, 
                prioritize symbolic rigor but note the discrepancy.
                Strategy: {strategy}
                Computational Results: {'; '.join(candidate_solutions) if candidate_solutions else 'None'}""",
                context=strategy
            )

            # Revise solution for errors (up to 2 iterations)
            current_solution = initial_solution
            for _ in range(2):
                critique = await self.generate(
                    instruction="""Critically analyze the following solution for: 
                    1. Algebraic or logical errors
                    2. Unjustified assumptions
                    3. Missing edge cases
                    4. Computational inconsistencies
                    If no errors, respond 'VERIFIED'. Otherwise, list errors and suggest corrections.""",
                    context=current_solution
                )
                if "VERIFIED" in critique.upper():
                    break
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the following issues: {critique}. 
                    Maintain all correct parts. Add missing justifications. Ensure final answer is boxed.""",
                    context=current_solution
                )

            refined_candidates.append(current_solution)

        # STEP 4: Ensemble synthesis with epistemic weighting
        final_answer = await self.ensemble(
            instruction="""Synthesize the most correct answer from the candidates below. Evaluate each on:
            1. Internal logical consistency
            2. Alignment with computational verification (if any)
            3. Minimality of assumptions
            4. Elegance and mathematical rigor
            If candidates conflict, identify the divergence point and resolve it by invoking a higher mathematical principle 
            (e.g., induction, symmetry, known theorem). Output ONLY the final integer answer between 000 and 999, boxed as \\boxed{answer}.
            Candidates:
            """ + "\n\n".join([f"Candidate {i+1}: {sol}" for i, sol in enumerate(refined_candidates)]),
            contexts_list=refined_candidates
        )

        return final_answer