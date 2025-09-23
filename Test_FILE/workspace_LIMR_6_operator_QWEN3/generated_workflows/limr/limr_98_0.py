# Workflow ID: limr_98_0
# Benchmark: limr
# Data Indices: [299, 37]

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

        # PHASE 1: STRUCTURAL ANALYSIS & STRATEGY PROPOSAL
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem:
            1. Classify the primary domain (algebra, geometry, combinatorics, number theory, optimization).
            2. Identify all variables, constraints, and implicit conditions.
            3. Determine if the solution requires construction, proof, optimization, or counting.
            4. Propose 3 distinct high-level solution strategies with brief rationale for each.
            5. Flag any potential pitfalls or non-obvious insights.
            Format as a structured report with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        strategy_branches = [
            "Develop Strategy 1 from the analysis in full mathematical detail. Show all steps, justify assumptions, and derive intermediate results.",
            "Develop Strategy 2 from the analysis in full mathematical detail. Show all steps, justify assumptions, and derive intermediate results.",
            "Develop Strategy 3 from the analysis in full mathematical detail. Show all steps, justify assumptions, and derive intermediate results."
        ]
        
        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_branches]
        )

        # PHASE 3: VALIDATION & ERROR CORRECTION
        validated_strategies = []
        for attempt in strategy_attempts:
            validated = await self.revise(
                instruction="""Critically evaluate this solution attempt:
                - Verify logical consistency of each step
                - Check computational accuracy (show recalculations if needed)
                - Ensure all constraints are satisfied
                - Identify any gaps, leaps, or unjustified assumptions
                - If repairable, provide corrected version with annotations
                - If fundamentally flawed, explain why and suggest alternative direction
                Return the most robust version possible.""",
                context=attempt
            )
            validated_strategies.append(validated)

        # PHASE 4: SYNTHESIS & INTEGRATION
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all validated strategies:
            - Combine correct steps from different approaches
            - Resolve contradictions by choosing most rigorous justification
            - Fill gaps using logical inference from problem constraints
            - Ensure complete, step-by-step derivation from start to final answer
            - Maintain mathematical rigor throughout
            - Output should be a single coherent solution narrative""",
            contexts_list=validated_strategies
        )

        # PHASE 5: COMPUTATIONAL VERIFICATION (PARALLEL)
        verification_task = self.programmer(
            instruction="""Extract the key mathematical expressions or conjectured final value from the solution.
            Write Python code to:
            1. Numerically verify the proposed solution with at least 3 test cases
            2. Check boundary conditions and edge cases
            3. If solution involves optimization, confirm via numerical methods
            4. Return 'VERIFIED' if all tests pass, else return detailed failure analysis
            IMPORTANT: If direct computation is infeasible, derive closed-form approximation then refine symbolically.""",
            context=synthesized_solution
        )

        # PHASE 6: ITERATIVE REFINEMENT (if needed)
        refined_solution = synthesized_solution
        for iteration in range(2):  # Max 2 refinement loops
            uncertainty_check = await self.generate(
                instruction="Does the current solution contain any unresolved ambiguities, unverified assumptions, or low-confidence steps? Answer YES/NO followed by brief explanation.",
                context=refined_solution
            )
            
            if "YES" in uncertainty_check.upper():
                refined_solution = await self.generate(
                    instruction=f"""The current solution has unresolved issues: {uncertainty_check}
                    Propose a fundamentally different approach leveraging advanced techniques not yet considered.
                    Consider: generating functions, modular arithmetic, geometric transformations, or combinatorial identities.
                    Develop this new approach in full mathematical detail.""",
                    context=refined_solution
                )
            else:
                break

        # PHASE 7: FINAL ANSWER EXTRACTION & FORMATTING
        final_answer = await self.revise(
            instruction="""Extract the final numerical answer from the solution:
            1. If symbolic, simplify to an exact integer
            2. If multiple candidates, justify selection with mathematical reasoning
            3. Format as three-digit integer (000-999) with leading zeros if needed
            4. If uncertain, state confidence level and top candidates
            5. Verify answer satisfies original problem constraints
            Return ONLY the three-digit integer unless confidence is below 90%, then explain briefly.""",
            context=refined_solution
        )

        # Extract just the integer answer using regex (handles both clean and explanatory outputs)
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d+', final_answer)
            for num in numbers:
                if len(num) <= 3:
                    return num.zfill(3)
            return "000"  # Ultimate fallback