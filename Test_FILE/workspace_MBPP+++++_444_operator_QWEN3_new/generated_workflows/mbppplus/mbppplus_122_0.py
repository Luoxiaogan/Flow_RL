# Workflow ID: mbppplus_122_0
# Benchmark: mbppplus
# Data Indices: [314, 106, 269]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Phase 1: Problem Decomposition & Strategy Classification
        decomposition = await self.generate(
            instruction="""Perform deep problem analysis. Answer:
            1. Input type and structure (list, int, string, etc.)?
            2. Required transformation/computation?
            3. Likely edge cases (empty, single, zero, negatives, duplicates)?
            4. 3 distinct algorithmic strategies (literal, mathematical, edge-first)?
            5. Expected return type and format?
            Format as structured JSON-like text with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""STRATEGY A: Direct Translation
                Convert problem description to literal code implementation.
                Problem Analysis: {decomposition}
                - Map requirements directly to Python constructs
                - Prioritize readability and directness
                - Include type handling and basic edge cases
                Output ONLY the function implementation as specified.""",
                context=""
            ),
            self.generate(
                instruction=f"""STRATEGY B: Mathematical Abstraction
                Identify underlying mathematical patterns or formulas.
                Problem Analysis: {decomposition}
                - Look for recurrence relations, bit manipulation, or algebraic shortcuts
                - Optimize for computational efficiency
                - Handle edge cases through mathematical invariants
                Output ONLY the function implementation as specified.""",
                context=""
            ),
            self.generate(
                instruction=f"""STRATEGY C: Edge-Case Driven Development
                Build solution by handling edge cases first.
                Problem Analysis: {decomposition}
                - Start with empty input, single element, zeros, negatives
                - Add complexity incrementally
                - Write defensive code with explicit conditionals
                - Ensure type consistency and boundary handling
                Output ONLY the function implementation as specified.""",
                context=""
            )
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # Phase 3: Independent Solution Refinement
        refinement_tasks = [
            self.revise(
                instruction="""Critique and improve this code:
                - Verify correctness against problem requirements
                - Add missing edge case handling (empty, single, zero, negatives)
                - Ensure return type matches expected format
                - Fix any type coercion or boundary issues
                - Optimize only if it doesn't sacrifice correctness
                Return ONLY the improved function implementation.""",
                context=sol
            ) for sol in strategy_solutions
        ]
        
        refined_solutions = await asyncio.gather(*refinement_tasks)

        # Phase 4: Ensemble Adjudication with Meta-Reasoning
        final_solution = await self.ensemble(
            instruction="""You are a senior code reviewer. Analyze these 3 solutions:
            For each solution, evaluate:
            1. Correctness on core requirements
            2. Edge case coverage (empty, single, zero, negatives, duplicates)
            3. Type consistency and return format
            4. Potential failure modes under hidden tests
            Then either:
            a) SELECT the single most robust solution, OR
            b) SYNTHESIZE a new solution combining the best elements
            Justify your choice with specific reasoning.
            Output ONLY the final function implementation as specified.""",
            contexts_list=refined_solutions
        )

        # Phase 5: Validation Loop (up to 2 iterations)
        current_solution = final_solution
        for validation_round in range(2):
            # Generate synthetic edge cases
            edge_cases = await self.generate(
                instruction=f"""Generate 5 synthetic test cases that would break a naive solution.
                Problem Analysis: {decomposition}
                Focus on:
                - Empty inputs
                - Single element cases
                - Zero values
                - Negative numbers
                - Type boundary conditions
                Format as Python assert statements.""",
                context=""
            )
            
            # Validate and revise if needed
            validated_solution = await self.revise(
                instruction=f"""Validate against these synthetic edge cases:
                {edge_cases}
                
                Does your solution handle ALL these cases correctly?
                If any case would fail, revise the code to fix the gaps.
                If already robust, return the solution unchanged.
                Return ONLY the function implementation.""",
                context=current_solution
            )
            
            # Break if no changes (converged)
            if validated_solution.strip() == current_solution.strip():
                break
            current_solution = validated_solution

        return current_solution