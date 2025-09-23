# Workflow ID: mbppplus_42_0
# Benchmark: mbppplus
# Data Indices: [83, 185]

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

        # Step 1: Decompose and classify the problem
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into:
            1. Problem type classification (mathematical, data structure, string, algorithm, edge-case heavy)
            2. Key input/output types and constraints
            3. List of potential edge cases (empty, single element, duplicates, boundaries)
            4. Required return type and format
            5. Any implied performance or efficiency constraints
            Return structured subproblems with dependencies if multi-step.""",
            context=""
        )

        # Extract classification for branching
        classification_analysis = await self.generate(
            instruction="""Based on the decomposition, classify this problem into one primary category:
            - 'mathematical_pattern': Involves formulas, sequences, repetitions
            - 'data_structure_op': Uses built-in modules (bisect, heapq, collections)
            - 'string_manipulation': Focus on string parsing, counting, patterns
            - 'algorithm_search': Requires custom search/sort logic
            - 'edge_case_heavy': Success depends on handling many boundary conditions
            Just output the category label.""",
            context=str(decomposition)
        )

        # Step 2: Parallel strategy generation based on classification
        strategies = []
        strategy_tasks = []

        # Always generate a mathematical/analytical approach
        strategy_tasks.append(
            self.generate(
                instruction="""Propose a mathematical or analytical solution strategy.
                Include: 
                - Pseudocode or formula derivation
                - Time/space complexity
                - How edge cases from decomposition are handled
                - Explicit return type enforcement
                - Why this approach is correct""",
                context=str(decomposition)
            )
        )

        # Always generate a library/util approach
        strategy_tasks.append(
            self.generate(
                instruction="""Propose a solution using Python standard library modules.
                Include:
                - Which modules/functions to use (bisect, itertools, collections, etc.)
                - How they apply to this problem
                - Edge case handling with library functions
                - Return type casting if needed
                - Efficiency justification""",
                context=str(decomposition)
            )
        )

        # Generate a brute-force/iterative approach as fallback
        strategy_tasks.append(
            self.generate(
                instruction="""Propose a straightforward iterative or brute-force solution.
                Include:
                - Step-by-step logic
                - How it handles every edge case from decomposition
                - Return type management
                - When this approach is preferable (simplicity, readability, edge-case safety)""",
                context=str(decomposition)
            )
        )

        # Execute all strategy generations in parallel
        strategy_results = await asyncio.gather(*strategy_tasks)
        strategies.extend(strategy_results)

        # Step 3: Ensemble synthesis of best strategy
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best solution strategy from the candidates.
            Evaluate each on:
            - Correctness for core logic
            - Edge case coverage
            - Efficiency (time/space)
            - Return type adherence
            - Code simplicity
            Combine the strongest elements. Output a unified strategy with:
            1. Chosen approach and why
            2. Final pseudocode
            3. Edge case handling plan
            4. Return type guarantee""",
            contexts_list=strategies
        )

        # Step 4: Generate code with strict constraints
        code_attempt = await self.programmer(
            instruction=f"""Implement the solution based on this strategy:
            {synthesized_strategy}
            
            STRICT REQUIREMENTS:
            - Use exact function signature from problem
            - Handle ALL edge cases listed in decomposition
            - Return correct type (int, list, tuple, etc.) as shown in examples
            - Include no extra output or print statements
            - Code must be self-contained (no external dependencies beyond standard library)
            - Optimize for correctness over brevity""",
            context=synthesized_strategy
        )

        # Step 5: Iterative refinement (max 2 iterations)
        current_code = code_attempt
        for iteration in range(2):
            revision = await self.revise(
                instruction=f"""Critically review this code:
                - Does it match the synthesized strategy?
                - Are all edge cases from decomposition handled?
                - Is return type correct and consistent?
                - Any off-by-one, type, or logic errors?
                - Can it be made more robust?
                If flaws found, rewrite ENTIRE function to fix them.
                If perfect, return unchanged.""",
                context=current_code
            )
            
            # Break if no changes (heuristic: if revision is same as input)
            if revision.strip() == current_code.strip():
                break
            current_code = revision

        # Step 6: Final validation
        validation = await self.generate(
            instruction="""Given this code and the original problem:
            1. List all potential failure modes or edge cases not handled
            2. Verify return type matches examples
            3. Check function signature is preserved
            If no issues, output exactly: 'VALID'
            Otherwise, list specific concerns.""",
            context=current_code
        )

        # If validation fails, fallback to brute-force approach
        if 'VALID' not in validation:
            fallback_code = await self.programmer(
                instruction=f"""Implement a defensive, brute-force solution that prioritizes correctness.
                Handle EVERY edge case explicitly.
                Use simple, readable logic.
                Double-check return type.
                Based on decomposition: {str(decomposition)}""",
                context=""
            )
            return fallback_code

        return current_code