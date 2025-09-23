# Workflow ID: mbppplus_168_0
# Benchmark: mbppplus
# Data Indices: [216, 267]

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

        # Phase 1: Problem Decomposition & Type Analysis
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into core components:
            1. Identify input parameter types and expected output type from signature
            2. Determine the core operation (filtering, transformation, search, calculation, etc.)
            3. List potential edge cases (empty inputs, single elements, boundary values, type edge cases)
            4. Note any implicit constraints (order preservation, type consistency, performance requirements)
            5. Identify domain-specific patterns (divisibility, string parsing, sequence operations, etc.)
            Return structured subproblems with clear dependencies.""",
            context=""
        )

        # Extract key constraints for dynamic instruction building
        constraints_analysis = await self.generate(
            instruction=f"""Based on this decomposition:
            {decomposition}
            
            Extract and summarize:
            - Required input/output type relationships
            - Critical edge cases to handle
            - Domain-specific operations needed
            - Any performance or style constraints
            Format as bullet points for use in code generation.""",
            context=str(decomposition)
        )

        # Phase 2: Parallel Solution Strategy Generation
        solution_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a FUNCTIONAL programming solution using built-in functions (filter, map, etc.):
                Constraints: {constraints_analysis}
                - Use lambda expressions where appropriate
                - Ensure type consistency with signature
                - Handle all edge cases identified
                - Return code only, no explanations""",
                context=constraints_analysis
            ),
            self.generate(
                instruction=f"""Generate an IMPERATIVE programming solution using explicit loops and conditionals:
                Constraints: {constraints_analysis}
                - Use clear, step-by-step logic
                - Include explicit edge case handling
                - Maintain input type consistency in output
                - Return code only, no explanations""",
                context=constraints_analysis
            ),
            self.generate(
                instruction=f"""Generate a SET-BASED or MATH-ORIENTED solution if applicable:
                Constraints: {constraints_analysis}
                - Leverage mathematical properties or set operations
                - Optimize for clarity and correctness
                - Handle edge cases explicitly
                - Return code only, no explanations""",
                context=constraints_analysis
            )
        )

        # Phase 3: Parallel Validation & Edge Case Testing
        validation_tasks = []
        for i, solution in enumerate(solution_strategies):
            validation_task = self.programmer(
                instruction=f"""Execute this solution against comprehensive edge cases:
                - Empty input
                - Single element input
                - All elements invalid
                - All elements valid
                - Boundary values
                - Type edge cases
                Return execution results including any errors or failures.
                Solution to test:
                {solution}""",
                context=solution,
                max_retries=1
            )
            validation_tasks.append(validation_task)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # Phase 4: Conditional Revision Loop
        revised_solutions = []
        for i, (solution, validation) in enumerate(zip(solution_strategies, validation_results)):
            current_solution = solution
            # Maximum 2 revision iterations
            for revision_round in range(2):
                if "error" in validation.lower() or "fail" in validation.lower():
                    current_solution = await self.revise(
                        instruction=f"""Revise this solution to fix the issues identified in validation:
                        Validation feedback: {validation}
                        Constraints to maintain: {constraints_analysis}
                        - Fix the specific errors mentioned
                        - Maintain type consistency
                        - Preserve core logic while addressing edge cases
                        - Return revised code only""",
                        context=current_solution
                    )
                    # Re-validate
                    validation = await self.programmer(
                        instruction=f"""Re-test revised solution against same edge cases.
                        Solution: {current_solution}""",
                        context=current_solution,
                        max_retries=1
                    )
                else:
                    break
            revised_solutions.append(current_solution)

        # Phase 5: Ensemble Selection with Multi-Criteria Evaluation
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Passes all edge case tests without errors
            2. Type Safety: Maintains input/output type consistency
            3. Readability: Clear, Pythonic, well-structured code
            4. Efficiency: Avoids unnecessary operations or allocations
            5. Robustness: Explicit handling of edge cases
            Return only the selected code, no explanations or markdown.""",
            contexts_list=revised_solutions
        )

        # Final cleanup: Ensure pure code output
        code_only = await self.generate(
            instruction="""Extract only the Python function code from this response.
            Remove any markdown, explanations, or non-code text.
            Ensure the function signature exactly matches the original problem.
            Return only the clean code block.""",
            context=final_solution
        )

        return code_only