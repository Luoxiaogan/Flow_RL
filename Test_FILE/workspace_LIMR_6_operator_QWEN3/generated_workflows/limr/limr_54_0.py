# Workflow ID: limr_54_0
# Benchmark: limr
# Data Indices: [270, 128]

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
        
        # PHASE 1: PROBLEM DECOMPOSITION & STRATEGY MAPPING
        decomposition_plan = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems with explicit dependencies. For each subproblem:
            - State what needs to be found/proved
            - Identify required mathematical domain (algebra, geometry, combinatorics, etc.)
            - List prerequisite subproblems by ID
            - Flag if it requires numerical computation
            - Note any potential trap doors or ambiguous conditions
            Output as structured dependency graph.""",
            context=""
        )
        
        # PHASE 2: PARALLEL SUBPROBLEM STRATEGY GENERATION
        strategy_tasks = []
        for i, subproblem in enumerate(decomposition_plan):
            strategy_task = self.generate(
                instruction=f"""For subproblem {subproblem['id']}: {subproblem['description']}
                Generate THREE distinct solution approaches:
                1. Algebraic/analytical approach
                2. Geometric/visual approach (if applicable)
                3. Combinatorial/computational approach (if applicable)
                For each approach:
                - Outline key steps
                - Identify required formulas/theorems
                - Estimate computational complexity
                - Flag potential failure points
                Format as clearly numbered strategies.""",
                context=subproblem['description']
            )
            strategy_tasks.append(strategy_task)
        
        raw_strategies = await asyncio.gather(*strategy_tasks)
        
        # PHASE 3: STRATEGY REFINEMENT & VALIDATION
        refined_strategies = []
        for i, strategy_set in enumerate(raw_strategies):
            refined = await self.revise(
                instruction=f"""Critique and improve these strategies for subproblem {decomposition_plan[i]['id']}:
                - Eliminate approaches that violate problem constraints
                - Strengthen weak steps with specific mathematical justifications
                - Add verification checks for critical assumptions
                - Simplify overly complex approaches without losing rigor
                - Ensure all approaches terminate in computable steps
                Preserve the three-strategy structure but make each bulletproof.""",
                context=strategy_set
            )
            refined_strategies.append(refined)
        
        # PHASE 4: PARALLEL SOLUTION ATTEMPTS WITH ADVERSARIAL VALIDATION
        solution_attempts = []
        validation_tasks = []
        
        for i, strategy_set in enumerate(refined_strategies):
            # Generate solution attempt
            solution_task = self.generate(
                instruction=f"""Execute the MOST PROMISING strategy from:
                {strategy_set}
                Show complete step-by-step reasoning.
                Box final intermediate result.
                If computation needed, explicitly state what to calculate.""",
                context=strategy_set
            )
            solution_attempts.append(solution_task)
            
            # Spawn adversarial validation in parallel
            validation_task = self.generate(
                instruction=f"""Play devil's advocate for this solution attempt:
                {strategy_set}
                - Identify the single most likely point of failure
                - Propose a counterexample or edge case
                - Suggest a verification test
                - If no flaws found, state "VERIFIED WITH HIGH CONFIDENCE"
                Be brutally honest but mathematically precise.""",
                context=strategy_set
            )
            validation_tasks.append(validation_task)
        
        solutions_and_validations = await asyncio.gather(
            *solution_attempts, *validation_tasks
        )
        solutions = solutions_and_validations[:len(solution_attempts)]
        validations = solutions_and_validations[len(solution_attempts):]
        
        # PHASE 5: SYNTHESIZE & RESOLVE CONFLICTS
        resolved_subproblems = []
        for i in range(len(solutions)):
            if "VERIFIED WITH HIGH CONFIDENCE" in validations[i] or "no flaws" in validations[i].lower():
                resolved_subproblems.append(solutions[i])
            else:
                # Conflict detected - ensemble multiple approaches
                conflict_resolution = await self.ensemble(
                    instruction=f"""Resolve conflicting solution paths for subproblem {decomposition_plan[i]['id']}:
                    Primary solution: {solutions[i]}
                    Validation critique: {validations[i]}
                    Generate revised solution that addresses critique while preserving valid insights.
                    If still uncertain, combine elements from multiple original strategies.
                    Output must be self-consistent and mathematically rigorous.""",
                    contexts_list=[solutions[i], validations[i]]
                )
                resolved_subproblems.append(conflict_resolution)
        
        # PHASE 6: DEPENDENCY-RESPECTING SYNTHESIS
        final_synthesis_context = "\n\n".join([
            f"Subproblem {decomposition_plan[i]['id']}: {resolved}"
            for i, resolved in enumerate(resolved_subproblems)
        ])
        
        integrated_solution = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into complete answer:
            {final_synthesis_context}
            
            - Respect dependency order (solve prerequisites first)
            - Combine intermediate results logically
            - Handle unit conversions or scaling if needed
            - Explicitly show how final answer emerges from components
            - If multiple answer candidates exist, resolve via mathematical consistency""",
            context=final_synthesis_context
        )
        
        # PHASE 7: COMPUTATIONAL VERIFICATION & CANONICALIZATION
        final_answer = await self.programmer(
            instruction=f"""Extract final numerical answer from this solution:
            {integrated_solution}
            
            Steps:
            1. Parse the final mathematical expression
            2. Compute exact value (no approximations)
            3. Convert to integer between 000-999
            4. If fractional, apply appropriate rounding as specified in problem
            5. Validate against original problem constraints
            6. Output ONLY the 3-digit integer, nothing else""",
            context=integrated_solution,
            max_retries=3
        )
        
        # PHASE 8: FINAL SANITY CHECK & FORMATTING
        canonical_answer = await self.revise(
            instruction="""Ensure answer meets ALL requirements:
            - Exactly 3 digits (pad with leading zeros if needed)
            - Integer value (no decimals, fractions, or units)
            - Matches problem's requested format
            - Falls within 000-999 range
            If any requirement violated, correct immediately.
            Output ONLY the 3-digit string.""",
            context=final_answer
        )
        
        # Extract just the 3-digit answer using regex to be safe
        match = re.search(r'\b\d{3}\b', canonical_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: take first 3 digits found
            digits = re.findall(r'\d', canonical_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            else:
                # Ultimate fallback - return 000 as error indicator
                return "000"