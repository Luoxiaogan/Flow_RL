# Workflow ID: limr_149_0
# Benchmark: limr
# Data Indices: [313, 319]

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

        # PHASE 1: META-CLASSIFICATION — Understand the problem's soul
        classification = await self.generate(
            instruction="""Perform deep problem classification. Analyze:
            1. Primary mathematical domain (algebra, combinatorics, number theory, geometry, etc.)
            2. Solution archetype: 
               - Direct computation? 
               - Clever substitution/identity? 
               - Proof/contradiction? 
               - Recursive/iterative structure?
               - Optimization/extremal principle?
            3. Expected answer format (must be integer 000-999 — flag if not)
            4. Key constraints, boundary conditions, or hidden symmetries
            5. Potential pitfalls or non-obvious transformations
            Output structured as:
            DOMAIN: [domain]
            ARCHETYPE: [archetype]
            CONSTRAINTS: [list]
            INSIGHT: [key non-obvious observation]
            """,
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION — Explore 3 distinct approaches
        strategy_instructions = [
            f"""Based on classification: {classification}
            Develop Strategy A: The most straightforward, textbook approach. 
            - What formulas, theorems, or standard methods apply?
            - Show step-by-step reasoning.
            - Identify where it might fail or be inefficient.""",
            
            f"""Based on classification: {classification}
            Develop Strategy B: The clever, non-obvious insight approach.
            - What substitution, symmetry, or transformation simplifies this?
            - Think outside standard methods — generating functions, invariants, probabilistic interpretations.
            - Why might this be more elegant or efficient?""",
            
            f"""Based on classification: {classification}
            Develop Strategy C: The computational/algorithmic approach.
            - How would you code this? What data structures or algorithms?
            - When would brute-force work? When must you find a closed form?
            - Outline pseudocode or mathematical reduction steps."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # PHASE 3: DECOMPOSE & SOLVE EACH STRATEGY (with embedded validation loops)
        async def solve_and_validate(strategy, strategy_id):
            for attempt in range(3):  # Max 3 refinement loops
                # Decompose based on strategy context
                decomposition = await self.decompose(
                    instruction=f"""Decompose this strategy into atomic, solvable subproblems:
                    Strategy: {strategy}
                    Classification: {classification}
                    Guidelines:
                    - Each subproblem must have clear inputs/outputs
                    - Order by dependency (prerequisites first)
                    - Include verification steps as subproblems
                    - Final subproblem must output integer 000-999""",
                    context=strategy
                )
                
                # Solve subproblems sequentially (respecting dependencies)
                solutions = {}
                for sub in decomposition:
                    deps = sub['dependencies'].split(',') if sub['dependencies'] else []
                    # Wait for dependencies (simplified: assume linear order)
                    dep_context = "\n".join([f"Subproblem {d}: {solutions.get(d, '')}" for d in deps if d in solutions])
                    
                    sub_solution = await self.generate(
                        instruction=f"""Solve subproblem: {sub['description']}
                        Classification: {classification}
                        Strategy: {strategy}
                        Dependencies: {dep_context}
                        Requirements:
                        - Show all steps
                        - Verify intermediate results
                        - If computational, prefer symbolic simplification first
                        - Output must be precise (no approximations)""",
                        context=dep_context
                    )
                    solutions[sub['id']] = sub_solution

                # Extract final answer from last subproblem
                final_sub_id = decomposition[-1]['id']
                candidate_answer = solutions[final_sub_id]
                
                # Validate answer format and consistency
                validation = await self.generate(
                    instruction=f"""Validate this solution:
                    Problem: {self.problem_text}
                    Classification: {classification}
                    Strategy: {strategy}
                    Candidate Answer: {candidate_answer}
                    Check:
                    1. Is the answer an integer between 000 and 999?
                    2. Does it satisfy all problem constraints?
                    3. Are there any logical gaps or arithmetic errors?
                    4. Does it match the expected archetype?
                    Output: VALID or INVALID with specific reasons.""",
                    context=candidate_answer
                )
                
                if "VALID" in validation:
                    return f"STRATEGY {strategy_id}: {candidate_answer}\nVALIDATION: {validation}"
                else:
                    # Revise strategy based on validation feedback
                    strategy = await self.revise(
                        instruction=f"""Revise strategy based on validation feedback:
                        Validation: {validation}
                        Original Strategy: {strategy}
                        Fix identified issues, strengthen weak points, reconsider approach if necessary.""",
                        context=strategy
                    )
            
            # If all attempts fail, return best effort with warning
            return f"STRATEGY {strategy_id} (UNVALIDATED): {candidate_answer}\nVALIDATION FAILED: {validation}"

        # Solve all strategies in parallel
        solved_strategies = await asyncio.gather(
            *[solve_and_validate(strat, chr(65+i)) for i, strat in enumerate(strategies)]
        )

        # PHASE 4: ENSEMBLE — Synthesize and select best answer
        final_answer = await self.ensemble(
            instruction="""Select the most credible answer from these strategies:
            - Prefer validated answers over unvalidated
            - Check for consensus among strategies
            - If conflict, analyze which strategy best respects problem constraints and classification
            - Extract the final integer answer (000-999) and justify selection
            - If no strategy is fully valid, select the least flawed and flag uncertainty
            Output format: 
            FINAL ANSWER: [integer]
            JUSTIFICATION: [concise reasoning]""",
            contexts_list=solved_strategies
        )

        # PHASE 5: FINAL EXTRACTION — Ensure clean integer output
        # Use regex to extract exactly the 3-digit integer
        match = re.search(r'\b\d{3}\b', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d+', final_answer)
            for num in numbers:
                if len(num) == 3:
                    return num
            # Ultimate fallback: return 000 (should never happen)
            return "000"