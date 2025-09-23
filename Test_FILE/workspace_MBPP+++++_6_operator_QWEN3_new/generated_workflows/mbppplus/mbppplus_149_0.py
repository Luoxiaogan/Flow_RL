# Workflow ID: mbppplus_149_0
# Benchmark: mbppplus
# Data Indices: [65, 54]

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

        # Phase 1: Problem Classification and Scope Analysis
        classification = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify problem type: string, mathematical, list/tuple, or logical
            2. Identify input/output data types and structures
            3. List all edge cases: empty inputs, single elements, boundaries, duplicates
            4. Determine if closed-form mathematical solution exists
            5. Assess complexity: simple iteration vs multi-step decomposition
            6. Note any constraints on time/space efficiency
            Format as structured JSON with keys: type, inputs, outputs, edge_cases, math_formula, complexity""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate Algorithmic Blueprint:
                Based on classification: {classification}
                - Define exact iteration space (range, collection, etc.)
                - Specify accumulator variable and initialization
                - Detail per-element operation (comparison, arithmetic, etc.)
                - Outline edge case handling logic
                - Return structured plan, not code""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Alternative Approach:
                Consider radically different strategy from obvious solution.
                If iterative, consider mathematical formula. If recursive, consider iterative.
                If using built-ins, consider manual implementation.
                Document trade-offs in readability vs efficiency.
                Format: [APPROACH]: ... [TRADEOFFS]: ...""",
                context=""
            )
        ]
        
        # Phase 3: Decomposition for Complex Problems
        decomposition = await self.decompose(
            instruction="""Break problem into minimal atomic steps:
            Each step must be implementable as single operation (loop, condition, calc).
            Identify dependencies between steps.
            Include explicit validation steps for edge cases.
            Return list of subproblems with dependencies.""",
            context=""
        )

        # Execute parallel strategies
        strategy_results = await asyncio.gather(*strategy_tasks)
        
        # Summarize strategies for ensemble
        summarized_strategies = []
        for i, strategy in enumerate(strategy_results):
            summary = await self.summarize(
                instruction=f"""Extract core algorithm and edge handling only.
                Remove examples and explanations. Format:
                [STRATEGY {i+1}]: [ALGORITHM]: ... [EDGE CASES]: ...""",
                context=strategy
            )
            summarized_strategies.append(summary)

        # Phase 4: Synthesize Best Approach
        synthesized = await self.ensemble(
            instruction="""Select and merge best elements from all strategies:
            - Prioritize correctness over cleverness
            - Choose approach that handles all edge cases
            - Prefer readability unless efficiency critical
            - Combine validation logic from all candidates
            Output must be complete implementation plan including:
            1. Function signature
            2. Variable initialization
            3. Main loop/condition structure
            4. Edge case handling
            5. Return statement""",
            contexts_list=summarized_strategies
        )

        # Phase 5: Generate Code with Strict Specifications
        code_attempt = await self.programmer(
            instruction=f"""Generate Python function with EXACT signature from problem.
            Requirements:
            - Handle all edge cases from classification: {classification}
            - Match data types exactly (list vs tuple vs scalar)
            - Use only basic loops/arithmetic - no external libraries
            - Include explicit input validation if needed
            - Return early on invalid inputs
            - Comment key sections for clarity
            - Follow PEP8 style
            Context: {synthesized}""",
            context=synthesized,
            max_retries=2
        )

        # Phase 6: Validation Loop
        for attempt in range(2):
            validation = await self.generate(
                instruction=f"""Validate code against edge cases:
                Code: {code_attempt}
                Edge cases from classification: {classification}
                Check:
                1. Does it handle empty inputs?
                2. Does it handle single elements?
                3. Does it handle boundary values?
                4. Does return type match exactly?
                5. Are there any type conversion errors?
                If any issues, list them specifically. If perfect, say 'VALIDATED'.""",
                context=code_attempt
            )
            
            if "VALIDATED" in validation:
                break
                
            # Revise with specific feedback
            code_attempt = await self.revise(
                instruction=f"""Fix these specific issues: {validation}
                Preserve correct parts of code. Only modify problematic sections.
                Maintain exact function signature and return types.
                Add comments explaining fixes.""",
                context=code_attempt
            )

        return code_attempt