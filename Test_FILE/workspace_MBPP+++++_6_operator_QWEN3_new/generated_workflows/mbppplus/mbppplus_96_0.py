# Workflow ID: mbppplus_96_0
# Benchmark: mbppplus
# Data Indices: [301, 373]

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

        # PHASE 1: Deep Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform comprehensive problem analysis. Extract:
            1. Core operation (what transformation or computation is needed?)
            2. Input/output data types and structures
            3. Edge cases (empty inputs, single elements, boundary values)
            4. Algorithmic paradigm (DP, greedy, brute force, set operations, etc.)
            5. Key constraints (order preservation, type consistency, performance)
            Format as JSON-like structure with clear keys.""",
            context=""
        )

        # PHASE 2: Complexity Classification (Conditional Branching)
        complexity = await self.generate(
            instruction="""Classify problem complexity based on:
            - Number of nested loops or recursive calls implied
            - Need for memoization or state tracking
            - Multiple conditional branches or edge cases
            - Data structure transformations required
            Return ONLY the word 'simple' or 'complex'.""",
            context=problem_analysis
        )

        # PHASE 3: Strategy Generation (Conditional Path)
        if "complex" in complexity.lower():
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction="""Break problem into minimal, executable subproblems.
                Each subproblem should be independently solvable and have clear dependencies.
                Focus on algorithmic steps, data transformations, and edge case handling.""",
                context=problem_analysis
            )
            
            # Solve subproblems in dependency order
            solutions = {}
            for sp in subproblems:
                deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                # Wait for dependencies (simplified - in practice would need topological sort)
                await asyncio.sleep(0)  # Yield control
                
                solution = await self.programmer(
                    instruction=f"""Solve subproblem: {sp['description']}
                    Context: {problem_analysis}
                    Dependencies: {deps}
                    Return only the code snippet or computational result needed.""",
                    context=problem_analysis
                )
                solutions[sp['id']] = solution
            
            # Synthesize final solution from subproblem solutions
            synthesis_context = "\n".join([f"{k}: {v}" for k, v in solutions.items()])
            code_attempt = await self.programmer(
                instruction=f"""Synthesize complete solution from subproblem solutions:
                {synthesis_context}
                
                Problem Context: {problem_analysis}
                Ensure function signature matches exactly. Handle all edge cases identified.
                Return ONLY the function implementation with necessary imports inside.""",
                context=synthesis_context
            )
        else:
            # Simple problem - direct code generation
            code_attempt = await self.programmer(
                instruction=f"""Generate solution based on analysis:
                {problem_analysis}
                
                Requirements:
                - Match exact function signature
                - Handle all identified edge cases
                - Use appropriate data types
                - Include necessary imports inside function if needed
                - Return ONLY the function implementation, no explanations""",
                context=problem_analysis
            )

        # PHASE 4: Code Validation and Refinement Loop
        refined_code = code_attempt
        for iteration in range(2):  # Maximum 2 refinement cycles
            critique = await self.revise(
                instruction="""Critically evaluate this code for:
                1. Correctness against edge cases (empty inputs, boundaries, duplicates)
                2. Adherence to specified return type and function signature
                3. Efficiency (avoid unnecessary complexity)
                4. Pythonic style and readability
                5. Proper handling of all constraints from problem analysis
                If issues found, rewrite entire code with fixes. Otherwise, return 'APPROVED'.""",
                context=refined_code
            )
            
            if "APPROVED" in critique:
                break
            refined_code = critique

        # PHASE 5: Ensemble Fallback for Persistent Issues
        if "APPROVED" not in critique:
            # Generate multiple solution strategies in parallel
            strategy_attempts = await asyncio.gather(
                self.programmer(
                    instruction=f"""Solve using alternative approach 1:
                    Problem: {problem_analysis}
                    Focus on simplicity and direct implementation.
                    Return ONLY function code.""",
                    context=problem_analysis
                ),
                self.programmer(
                    instruction=f"""Solve using alternative approach 2:
                    Problem: {problem_analysis}
                    Focus on robustness and edge case handling.
                    Return ONLY function code.""",
                    context=problem_analysis
                ),
                self.programmer(
                    instruction=f"""Solve using alternative approach 3:
                    Problem: {problem_analysis}
                    Focus on efficiency and minimal operations.
                    Return ONLY function code.""",
                    context=problem_analysis
                )
            )
            
            # Select best solution via ensemble
            refined_code = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Correctness (handles all edge cases)
                2. Adherence to function signature
                3. Code clarity and maintainability
                4. Efficiency
                Return ONLY the selected code, no explanations.""",
                contexts_list=strategy_attempts
            )

        return refined_code