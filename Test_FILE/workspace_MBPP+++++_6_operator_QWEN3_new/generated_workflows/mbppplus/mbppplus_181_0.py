# Workflow ID: mbppplus_181_0
# Benchmark: mbppplus
# Data Indices: [88, 49]

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

        # Phase 1: Problem Understanding & Classification
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis. Identify:
            1. Input types and structures (list, tuple, set, string, etc.)
            2. Output requirements and type
            3. Key operations needed (sorting, searching, DP, graph traversal, etc.)
            4. Edge cases to consider (empty, single element, duplicates, boundaries)
            5. Algorithmic paradigms likely applicable (greedy, DP, BFS, etc.)
            6. Constraints and invariants
            Output as structured JSON with keys: input_type, output_type, operations, edge_cases, paradigms, constraints""",
            context=""
        )

        # Phase 2: Decompose into subproblems
        decomposition = await self.decompose(
            instruction="""Break the problem into logical subproblems. For each subproblem:
            - Describe what it accomplishes
            - List its dependencies (other subproblems it relies on)
            - Indicate if it's about input validation, core logic, edge handling, or output formatting
            Prioritize clarity and separation of concerns.""",
            context=problem_analysis
        )

        # Extract paradigms for parallel strategy generation
        paradigms_analysis = await self.generate(
            instruction="""From the problem analysis, extract the 2-4 most promising algorithmic paradigms.
            For each, write a 100-word instruction on how to approach the problem using that paradigm.
            Format as JSON list of objects with keys: paradigm_name, instruction""",
            context=problem_analysis
        )

        try:
            paradigms_data = json.loads(paradigms_analysis)
            paradigm_instructions = [item["instruction"] for item in paradigms_data]
        except:
            # Fallback if JSON parsing fails
            paradigm_instructions = [
                "Solve using dynamic programming principles",
                "Solve using greedy algorithm approach",
                "Solve using breadth-first search or graph traversal",
                "Solve using sorting and two-pointer technique"
            ]

        # Phase 3: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""{instr}
                - Ensure type consistency with problem requirements
                - Handle all edge cases identified in analysis
                - Return exactly the required data type
                - Write clean, efficient, and readable code
                - Include comments for complex logic""",
                context=problem_analysis
            ) for instr in paradigm_instructions
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Phase 4: Code Generation & Validation Loop
        validated_solutions = []
        for candidate in strategy_candidates:
            code_result = await self.programmer(
                instruction="""Generate executable Python code that solves the problem.
                - Match exact function signature from problem
                - Include necessary imports
                - Handle edge cases
                - Return correct data type
                - Must be self-contained""",
                context=candidate,
                max_retries=2
            )
            
            # Validate with edge case generation
            edge_validation = await self.generate(
                instruction=f"""Given this solution:
                {code_result}
                
                Generate 5 edge case test scenarios not mentioned in the problem.
                For each, predict expected output and explain why.
                If any edge case would fail, suggest revision.""",
                context=problem_analysis
            )
            
            if "fail" not in edge_validation.lower() and "error" not in edge_validation.lower():
                validated_solutions.append(code_result)
            else:
                # Revise once if validation suggests issues
                revised = await self.revise(
                    instruction=f"""Fix issues identified in edge case validation:
                    {edge_validation}
                    Ensure robustness and correctness.""",
                    context=code_result
                )
                validated_solutions.append(revised)

        # Phase 5: Ensemble Selection
        if len(validated_solutions) > 1:
            final_solution = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Correctness (handles all edge cases)
                2. Efficiency (time/space complexity)
                3. Readability and maintainability
                4. Adherence to problem constraints
                5. Type consistency
                If multiple are equally good, synthesize the best elements into one solution.""",
                contexts_list=validated_solutions
            )
        elif len(validated_solutions) == 1:
            final_solution = validated_solutions[0]
        else:
            # Fallback: Generate with broader approach
            final_solution = await self.generate(
                instruction="""Generate a robust, general solution.
                - Use conservative, well-tested approaches
                - Prioritize correctness over cleverness
                - Include comprehensive edge case handling
                - Match exact function signature and return type""",
                context=problem_analysis
            )

        return final_solution