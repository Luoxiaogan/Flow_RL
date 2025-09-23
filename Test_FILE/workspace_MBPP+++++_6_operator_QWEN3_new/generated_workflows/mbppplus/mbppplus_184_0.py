# Workflow ID: mbppplus_184_0
# Benchmark: mbppplus
# Data Indices: [16, 62]

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

        # PHASE 1: Problem Classification and Structural Analysis
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Classify problem type: optimization, enumeration, modular arithmetic, greedy, simulation, etc.
            2. Identify key variables, constraints, and invariants.
            3. Detect edge cases: zero inputs, empty collections, single elements, duplicates, negatives, boundaries.
            4. Propose 2-3 distinct solution strategies with pros/cons (efficiency, correctness, complexity).
            5. Estimate difficulty and likely failure points.
            Format as structured analysis with clear sections.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Exploration
        strategy_instructions = [
            """Develop Strategy 1 based on classification. Focus on mathematical/algebraic approach.
            - Derive formulas or invariants
            - Handle edge cases explicitly
            - Draft pseudocode with step-by-step logic
            - Anticipate test cases beyond examples""",
            """Develop Strategy 2 based on classification. Focus on algorithmic/iterative approach.
            - Consider brute-force, greedy, or search methods
            - Analyze time/space complexity
            - Handle edge cases explicitly
            - Draft pseudocode with clear termination conditions""",
            """Develop Strategy 3 based on classification. Focus on heuristic or hybrid approach.
            - Combine insights from different domains
            - Optimize for readability and maintainability
            - Include defensive programming for unexpected inputs
            - Draft pseudocode with error handling"""
        ]

        strategy_contexts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # PHASE 3: Strategy Refinement and Critique
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically improve this strategy:
                - Fix logical gaps or edge-case vulnerabilities
                - Strengthen handling of zero, empty, boundary conditions
                - Ensure type consistency and return value correctness
                - Simplify without sacrificing robustness
                - Align with problem's exact function signature requirements""",
                context=strat
            ) for strat in strategy_contexts]
        )

        # PHASE 4: Strategy Synthesis and Selection
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize or select the optimal strategy:
            1. Evaluate each strategy on: correctness, edge-case coverage, efficiency, simplicity.
            2. Prefer strategies that handle all provided test cases and anticipate hidden ones.
            3. If complementary strengths exist, merge them into a hybrid approach.
            4. Output final unified strategy with clear implementation steps and edge-case handling.
            5. Explicitly state how zero, empty, and boundary cases are managed.""",
            contexts_list=refined_strategies
        )

        # PHASE 5: Code Implementation with Iterative Refinement
        final_code = None
        last_error = None
        
        for attempt in range(3):
            try:
                code_attempt = await self.programmer(
                    instruction=f"""Implement solution based on this strategy:
                    {synthesized_strategy}
                    
                    STRICT REQUIREMENTS:
                    - Use EXACT function signature from problem
                    - Handle ALL edge cases: zero, empty, single-element, negatives, boundaries
                    - Return correct data types (int, float, list, tuple as specified)
                    - No unnecessary imports or complexity
                    - Code must pass provided test cases and generalize to hidden ones
                    - Include defensive checks for invalid inputs if applicable""",
                    context=synthesized_strategy,
                    max_retries=1
                )
                
                # Extract code block if present
                code_match = re.search(r'