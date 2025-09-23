# Workflow ID: mbppplus_56_0
# Benchmark: mbppplus
# Data Indices: [66, 345]

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

        # PHASE 1: Problem Classification & Requirement Extraction
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it by:
            1. Primary operation type (e.g., counting, filtering, transforming, ranking, validating)
            2. Data structures involved (string, list, tuple, set, dict)
            3. Key constraints (order preservation, uniqueness, case sensitivity, etc.)
            4. Edge cases to consider (empty inputs, single elements, duplicates, type boundaries)
            5. Expected return type and format
            Provide a structured, detailed classification that will guide solution strategy.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Break this problem into essential subproblems with clear dependencies:
            - Subproblem 1: Input validation and edge case handling
            - Subproblem 2: Core algorithmic computation
            - Subproblem 3: Output formatting and type compliance
            Each subproblem should be self-contained with explicit success criteria.""",
            context=classification
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_instructions = [
            """Generate a solution using Python's built-in libraries and optimized functions (e.g., collections.Counter, set operations, itertools). 
            Prioritize readability and standard library usage. Include comprehensive edge case handling.""",
            
            """Generate a solution using explicit loops and manual iteration. Avoid external libraries. 
            Focus on clarity of logic and step-by-step processing. Handle all edge cases explicitly.""",
            
            """Generate a solution using functional programming constructs (list comprehensions, map/filter, lambda). 
            Emphasize conciseness and Pythonic style. Ensure robustness against edge cases."""
        ]

        strategy_context = f"Problem Classification: {classification}\nDecomposition: {str(decomposition)}"
        
        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=strategy_context) for instr in strategy_instructions]
        )

        # PHASE 3: Parallel Code Generation & Execution
        code_attempts = []
        for i, strategy in enumerate(strategies):
            try:
                code_result = await self.programmer(
                    instruction=f"""Implement the solution based on this strategy:
                    {strategy}
                    
                    Requirements:
                    - Handle all edge cases identified in classification
                    - Match exact return type specified in problem
                    - Include necessary imports
                    - Be production-ready and efficient
                    
                    If implementation fails, return detailed error explanation.""",
                    context=strategy,
                    max_retries=2
                )
                code_attempts.append(code_result)
            except Exception as e:
                code_attempts.append(f"ERROR in attempt {i+1}: {str(e)}")

        # PHASE 4: Ensemble Validation & Selection
        final_solution = await self.ensemble(
            instruction="""Evaluate all candidate solutions and select the best one based on:
            1. Correctness (handles all edge cases, matches expected output format)
            2. Efficiency (optimal time/space complexity)
            3. Readability and maintainability
            4. Adherence to Python best practices
            If candidates disagree on outputs, identify the most robust solution.
            Return ONLY the final selected code implementation with imports.""",
            contexts_list=code_attempts
        )

        # PHASE 5: Final Refinement & Type Enforcement
        refined_solution = await self.revise(
            instruction="""Critically review the selected solution and ensure:
            1. All necessary imports are included at the top
            2. Function signature exactly matches the required specification
            3. Return type is precisely as expected (list, tuple, set, etc.)
            4. Edge cases (empty inputs, single elements) are explicitly handled
            5. Code is clean, efficient, and follows Python conventions
            Return ONLY the final refined code - nothing else.""",
            context=final_solution
        )

        # Extract just the code block if it's wrapped in markdown
        code_match = re.search(r'