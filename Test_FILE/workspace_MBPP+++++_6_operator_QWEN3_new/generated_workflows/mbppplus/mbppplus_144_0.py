# Workflow ID: mbppplus_144_0
# Benchmark: mbppplus
# Data Indices: [191, 19]

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

        # Stage 1: Deep Problem Interpretation
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:
            1. Exact task specification: What is the function supposed to compute or return?
            2. Input/output types: What data types are involved? Are there type constraints?
            3. Edge cases: What are the boundary conditions? (empty inputs, single elements, duplicates, negatives, etc.)
            4. Algorithmic category: Is this a combinatorial, mathematical, string, or data structure problem?
            5. Hidden constraints: What unstated requirements might exist based on test cases?
            6. Expected complexity: Should the solution be optimized for time, space, or simplicity?
            Present your analysis in a structured JSON-like format with clear section headers.""",
            context=""
        )

        # Stage 2: Problem Decomposition
        subproblems = await self.decompose(
            instruction="""Break down this problem into minimal, executable subproblems. For each subproblem:
            - Describe what needs to be computed or decided
            - Specify its dependencies (which other subproblems must be solved first)
            - Indicate whether it requires mathematical computation, logical validation, or data transformation
            - Flag if it involves edge case handling
            Prioritize subproblems that handle edge cases or type validation first.""",
            context=problem_analysis
        )

        # Stage 3: Parallel Solution Strategy Generation
        strategy_instructions = [
            """Develop a mathematical/algorithmic solution strategy. Focus on:
            - Formalizing the problem as equations or recurrence relations
            - Identifying optimal data structures
            - Specifying time/space complexity
            - Handling edge cases mathematically""",
            
            """Develop a practical/iterative solution strategy. Focus on:
            - Step-by-step procedural approach
            - Concrete variable names and loop structures
            - Early termination conditions
            - Defensive programming for edge cases""",
            
            """Develop a pattern-based solution strategy. Focus on:
            - Recognizing similar problems or templates
            - Leveraging built-in Python functions or idioms
            - Code readability and maintainability
            - Common pitfalls to avoid"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_instructions]
        )

        # Stage 4: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best elements from all solution strategies. Your synthesis must:
            1. Combine the most robust algorithmic approach with the clearest implementation plan
            2. Explicitly address all edge cases identified in the problem analysis
            3. Specify exact variable names, loop conditions, and return statements
            4. Include type annotations and data structure choices
            5. Justify why this synthesis is superior to any individual strategy
            Output a complete, step-by-step implementation plan ready for code generation.""",
            contexts_list=strategy_attempts
        )

        # Stage 5: Code Generation with Validation Loop
        max_attempts = 3
        code_solution = None
        validation_feedback = ""

        for attempt in range(max_attempts):
            if attempt == 0:
                code_context = synthesized_strategy
            else:
                code_context = f"Previous attempt: {code_solution}\n\nFeedback: {validation_feedback}\n\nRevise the solution:"

            code_solution = await self.programmer(
                instruction="""Generate Python code that solves the problem exactly as specified. Requirements:
                - Use the exact function signature from the problem
                - Handle all edge cases explicitly
                - Include necessary imports inside the function if needed
                - Return the correct data type (list, tuple, set, etc.)
                - No print statements or interactive elements
                - Code must be self-contained and immediately executable
                - Prioritize correctness over cleverness""",
                context=code_context,
                max_retries=1
            )

            # Validate the solution against predicted edge cases
            validation_feedback = await self.generate(
                instruction=f"""Critically evaluate this code solution:
                1. Does it handle all edge cases from the original analysis?
                2. Are there any type mismatches or boundary condition failures?
                3. Could it fail on empty inputs, single elements, or extreme values?
                4. Is the algorithm logically sound for all test cases?
                5. Are there any off-by-one errors or infinite loop risks?
                If no issues found, respond with 'VALIDATED'. Otherwise, list specific, actionable fixes.""",
                context=f"Problem Analysis: {problem_analysis}\n\nCode: {code_solution}"
            )

            if "VALIDATED" in validation_feedback.upper():
                break

        # Stage 6: Final Refinement and Output
        final_code = await self.revise(
            instruction="""Final polish pass. Ensure:
            - Code is clean, readable, and follows Python best practices
            - Variable names are descriptive
            - Logic is straightforward and maintainable
            - All edge cases are handled gracefully
            - Return type exactly matches requirements
            - No unnecessary complexity or over-engineering
            Make minimal changes only if absolutely necessary.""",
            context=code_solution
        )

        return final_code