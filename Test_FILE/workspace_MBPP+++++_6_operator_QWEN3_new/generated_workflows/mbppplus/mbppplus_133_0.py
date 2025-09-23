# Workflow ID: mbppplus_133_0
# Benchmark: mbppplus
# Data Indices: [183, 59]

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

        # Step 1: Extract comprehensive problem specification
        specification = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem. Extract:
            1. Exact function signature (name, parameters, return type)
            2. Explicit requirements and implicit constraints
            3. Edge cases that must be handled (empty inputs, single elements, duplicates, type boundaries)
            4. Data type expectations (list vs tuple vs set, order preservation)
            5. Potential ambiguities needing resolution
            6. Complexity rating (1-5) based on logical branches and edge case density
            Format as structured JSON with keys: signature, constraints, edge_cases, data_types, ambiguities, complexity_rating""",
            context=""
        )

        # Step 2: Classify problem complexity to adapt workflow depth
        complexity_analysis = await self.generate(
            instruction=f"""Based on this specification:
            {specification}
            
            Determine if this problem requires:
            - Simple direct solution (complexity <= 2)
            - Parallel solution exploration (complexity 3-4)
            - Full decomposition into subproblems (complexity 5)
            Also identify if the problem involves: mathematical operations, list/tuple manipulations, string processing, or logical conditions.
            Return JSON with keys: workflow_strategy (direct|parallel|decomposed), domain_categories""",
            context=specification
        )
        
        complexity_data = json.loads(complexity_analysis)
        strategy = complexity_data.get("workflow_strategy", "parallel")

        # Step 3a: For decomposable problems, break into subproblems
        if strategy == "decomposed":
            decomposition = await self.decompose(
                instruction=f"""Break this problem into minimal atomic subproblems:
                - Each subproblem must have clear input/output contract
                - Specify dependencies between subproblems
                - Ensure collectively they solve the original problem
                Use the specification: {specification}""",
                context=specification
            )
            
            # Solve each subproblem recursively (depth-limited)
            subproblem_solutions = []
            for i, subproblem in enumerate(decomposition[:3]):  # Limit depth
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem: {subproblem['description']}
                    Adhere to these constraints: {specification}
                    Return only the implementation code with proper signature""",
                    context=specification
                )
                subproblem_solutions.append(sub_solution)
            
            # Summarize integration logic
            integration_plan = await self.summarize(
                instruction="""Create integration plan for subproblem solutions:
                - How do outputs of subproblems feed into each other?
                - What is the final composition logic?
                - Handle type conversions and edge case propagation""",
                context="\n".join(subproblem_solutions)
            )
            
            # Generate final integrated solution
            final_attempt = await self.programmer(
                instruction=f"""Implement complete solution by integrating subproblem solutions:
                Integration plan: {integration_plan}
                Original specification: {specification}
                Test with these edge cases: [], [0], [-1], [1,1,1], [2,2,2]""",
                context=integration_plan,
                max_retries=2
            )
            return final_attempt

        # Step 3b: For parallel exploration strategy
        elif strategy == "parallel":
            # Generate three diverse solution approaches in parallel
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve using functional programming style:
                    - Use generators, comprehensions, built-ins
                    - Prioritize readability and Pythonic style
                    - Handle all edge cases from specification: {specification}
                    Return only the function implementation""",
                    context=specification
                ),
                self.generate(
                    instruction=f"""Solve using imperative style:
                    - Use explicit loops and conditionals
                    - Add defensive checks for edge cases
                    - Prioritize robustness over brevity
                    Specification: {specification}
                    Return only the function implementation""",
                    context=specification
                ),
                self.generate(
                    instruction=f"""Solve using mathematical/set operations:
                    - Use min/max, set theory, arithmetic optimizations
                    - Prioritize computational efficiency
                    - Handle edge cases specified in: {specification}
                    Return only the function implementation""",
                    context=specification
                )
            )

            # Critique each solution for robustness
            critiques = await asyncio.gather(*[
                self.revise(
                    instruction=f"""Critique this solution for:
                    1. Type consistency (match expected return type from spec)
                    2. Edge case coverage (test with: empty, singleton, duplicates, negatives)
                    3. Efficiency (avoid O(n^2) when unnecessary)
                    4. Adherence to all constraints in specification: {specification}
                    If flaws found, rewrite solution to fix them.
                    Original solution: """,
                    context=attempt
                ) for attempt in solution_attempts
            ])

            # Execute revised solutions with synthetic edge case testing
            execution_results = []
            for i, critique in enumerate(critiques):
                try:
                    result = await self.programmer(
                        instruction=f"""Implement this solution, incorporating the critique:
                        {critique}
                        Test with edge cases: [], [0], [-1, -2], [1,1,1], [2,2,2]
                        Return implementation that passes all tests.""",
                        context=critique,
                        max_retries=2
                    )
                    execution_results.append(result)
                except Exception as e:
                    execution_results.append(f"EXECUTION_FAILED_{i}: {str(e)}")

            # Ensemble best solution
            final_solution = await self.ensemble(
                instruction=f"""Select or synthesize the best solution from candidates:
                - Prefer solutions that handle most edge cases
                - Favor readability if multiple are correct
                - Merge robustness features if solutions complement each other
                - Must match exact function signature from specification: {specification}
                Candidates: {json.dumps(execution_results)}""",
                contexts_list=[str(r) for r in execution_results if "EXECUTION_FAILED" not in str(r)]
            )
            return final_solution

        # Step 3c: For simple problems, direct solution with edge case testing
        else:  # strategy == "direct"
            direct_solution = await self.programmer(
                instruction=f"""Implement solution directly:
                - Follow specification exactly: {specification}
                - Test with edge cases: [], [0], [-1], [1], [2]
                - Ensure type consistency and handle all constraints
                Return only the function implementation that passes tests.""",
                context=specification,
                max_retries=3
            )
            return direct_solution