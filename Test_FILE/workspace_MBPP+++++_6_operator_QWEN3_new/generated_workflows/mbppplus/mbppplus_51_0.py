# Workflow ID: mbppplus_51_0
# Benchmark: mbppplus
# Data Indices: [290, 299]

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
        import re
        import math

        # Phase 1: Problem Classification and Complexity Assessment
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:
            1. Classify the problem type (numerical, string, list, logical, etc.)
            2. Identify the core operation required (comparison, transformation, validation, etc.)
            3. Estimate complexity (trivial, moderate, complex)
            4. List potential edge cases (empty inputs, negatives, zeros, type boundaries)
            5. Suggest 2-3 possible solution strategies
            Format as structured JSON with keys: type, operation, complexity, edge_cases, strategies""",
            context=""
        )

        # Phase 2: Conditional Processing - Simple vs Complex
        if "trivial" in classification.lower() or "simple" in classification.lower():
            # Direct solution for simple problems
            solution = await self.programmer(
                instruction=f"""Generate a Python function that solves this problem:
                {self.problem_text}
                
                Requirements:
                - Handle all edge cases mentioned in classification
                - Match exact function signature
                - Return correct data type
                - Include necessary imports
                - Write clean, efficient code""",
                context=classification,
                max_retries=3
            )
            return solution

        # Phase 3: Decomposition for Complex Problems
        subproblems = await self.decompose(
            instruction="""Break this problem into atomic, independently solvable subproblems.
            Each subproblem should:
            - Focus on one specific aspect (e.g., input validation, core computation, edge case handling)
            - Be solvable with a single function or operation
            - Have clear inputs and outputs
            - Include any dependencies on other subproblems
            Return as list of dictionaries with 'id', 'description', 'dependencies'""",
            context=classification
        )

        # Phase 4: Parallel Strategy Generation
        strategy_tasks = []
        for i in range(3):  # Generate 3 different approaches
            task = self.generate(
                instruction=f"""Develop solution strategy {i+1} for this problem:
                - Use a different algorithmic approach than other strategies
                - Consider trade-offs between readability, efficiency, and robustness
                - Explicitly address edge cases from classification
                - Outline step-by-step implementation plan
                Problem context: {classification}""",
                context=""
            )
            strategy_tasks.append(task)
        
        strategies = await asyncio.gather(*strategy_tasks)

        # Phase 5: Parallel Implementation
        implementation_tasks = []
        for i, strategy in enumerate(strategies):
            task = self.programmer(
                instruction=f"""Implement this solution strategy:
                {strategy}
                
                Requirements:
                - Exact function signature as specified
                - Handle all edge cases
                - Include necessary imports
                - Return correct data type
                - Add comments explaining key decisions""",
                context=strategy,
                max_retries=2
            )
            implementation_tasks.append(task)
        
        implementations = await asyncio.gather(*implementation_tasks)

        # Phase 6: Validation and Critique
        critique_tasks = []
        for implementation in implementations:
            critique = await self.generate(
                instruction=f"""Critically evaluate this implementation:
                - Does it handle all edge cases?
                - Is the return type correct?
                - Are there any logical errors?
                - Can it be optimized?
                - Does it match the function signature?
                Implementation: {implementation}""",
                context=implementation
            )
            critique_tasks.append(critique)
        
        critiques = await asyncio.gather(*critique_tasks)

        # Phase 7: Targeted Revision
        revised_implementations = []
        for i, (implementation, critique) in enumerate(zip(implementations, critiques)):
            if "error" in critique.lower() or "issue" in critique.lower():
                revised = await self.revise(
                    instruction=f"""Fix the issues identified in this critique:
                    {critique}
                    
                    Improve the implementation while preserving its core approach.
                    Ensure all edge cases are handled and return type is correct.""",
                    context=implementation
                )
                revised_implementations.append(revised)
            else:
                revised_implementations.append(implementation)

        # Phase 8: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Select the best solution from these candidates:
            - Prioritize correctness and edge case handling
            - Prefer cleaner, more readable code
            - Consider efficiency but don't sacrifice correctness
            - Ensure exact function signature match
            - Verify return type consistency
            Return only the final implementation code""",
            contexts_list=revised_implementations
        )

        # Phase 9: Final Validation and Type Checking
        final_validation = await self.generate(
            instruction=f"""Perform final validation on this solution:
            - Verify function signature matches exactly
            - Confirm return type is correct
            - Check that all imports are included
            - Ensure no placeholder code remains
            - Validate against edge cases from initial classification
            Solution: {final_solution}""",
            context=final_solution
        )

        if "error" in final_validation.lower() or "incorrect" in final_validation.lower():
            final_solution = await self.revise(
                instruction=f"""Fix any remaining issues identified in validation:
                {final_validation}
                
                Ensure perfect compliance with problem requirements.
                Return only the corrected implementation.""",
                context=final_solution
            )

        return final_solution