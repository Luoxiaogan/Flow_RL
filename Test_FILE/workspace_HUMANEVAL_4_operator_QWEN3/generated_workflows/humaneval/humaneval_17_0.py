# Workflow ID: humaneval_17_0
# Benchmark: humaneval
# Data Indices: [145, 48]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Phase 1: Problem Analysis and Multi-Perspective Solution Generation
        analysis_instruction = """
        Perform deep structural analysis of the code generation problem:
        1. Extract the exact function signature and return type requirements
        2. Identify all examples in the docstring and what they reveal about edge cases
        3. Determine the core algorithmic pattern (sorting, filtering, mathematical, string manipulation, etc.)
        4. Note any stability requirements, ordering constraints, or special handling (negative numbers, empty inputs, etc.)
        5. Classify the problem type and suggest 2-3 different implementation strategies
        6. Highlight potential pitfalls or subtle requirements that might be missed
        Output should be a comprehensive, structured analysis.
        """
        analysis = await self.generate(instruction=analysis_instruction, context="")

        # Generate multiple solution attempts from different perspectives
        solution_instructions = [
            """
            Generate a solution focusing on mathematical/formulaic approach:
            - Derive any underlying mathematical patterns from the examples
            - Use explicit calculations rather than built-in functions when possible
            - Handle edge cases explicitly (empty inputs, negatives, zeros)
            - Ensure return types match exactly (int vs float, list ordering)
            - Include detailed comments explaining the logic
            """,
            """
            Generate a solution focusing on algorithmic/data structure approach:
            - Consider sorting, filtering, mapping, or other list operations
            - Use appropriate key functions or comparators
            - Preserve stability if required (original order for ties)
            - Optimize for clarity and correctness over performance
            - Include inline comments explaining key decisions
            """,
            """
            Generate a solution by directly generalizing from the examples:
            - Analyze each example input-output pair to infer transformation rules
            - Handle special cases shown in examples (like negative numbers or empty lists)
            - Ensure the solution would work for unseen inputs following the same pattern
            - Include assertions or comments that map code sections to example behaviors
            """
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.generate(instruction=instr, context=analysis)
            for instr in solution_instructions
        ]
        initial_solutions = await asyncio.gather(*solution_tasks)

        # Phase 2: Adversarial Critique - Generate critiques for each solution
        critique_instructions = [
            f"""
            Critically evaluate Solution {i+1} for correctness and completeness:
            1. Does it handle ALL examples shown in the docstring?
            2. Does it address edge cases (empty inputs, single elements, negatives, zeros)?
            3. Are return types correct (int vs float, exact list ordering)?
            4. Does it preserve stability (original order for ties) if required?
            5. Are there any logical flaws or potential bugs?
            6. Is the solution overfitting to examples rather than generalizing?
            Provide specific, actionable feedback for improvement.
            """
            for i in range(len(initial_solutions))
        ]

        critique_tasks = [
            self.generate(instruction=instr, context=sol)
            for instr, sol in zip(critique_instructions, initial_solutions)
        ]
        critiques = await asyncio.gather(*critique_tasks)

        # Phase 3: Revision - Improve each solution based on critiques
        revision_tasks = [
            self.revise(
                instruction=f"""
                Revise the solution based on this critique:
                {critique}
                
                Specific requirements:
                - Fix all identified issues while preserving correct parts
                - Ensure the solution is general (not hardcoded for examples)
                - Maintain exact function signature and return types
                - Add comments explaining how edge cases are handled
                - Optimize for clarity and correctness
                """,
                context=solution
            )
            for solution, critique in zip(initial_solutions, critiques)
        ]
        revised_solutions = await asyncio.gather(*revision_tasks)

        # Phase 4: Edge Case Probing - Generate additional test cases and validate
        edge_case_analysis = await self.generate(
            instruction="""
            Based on the problem specification and examples, generate 3-5 additional edge cases
            that are not explicitly shown but are likely to be in hidden tests.
            Consider: empty inputs, single elements, maximum/minimum values, repeated values,
            negative numbers, zeros, and boundary conditions.
            For each edge case, explain why it's important and what it tests.
            """,
            context=analysis
        )

        # Validate revised solutions against edge cases (conceptually)
        validation_tasks = [
            self.generate(
                instruction=f"""
                Given these edge cases:
                {edge_case_analysis}
                
                Does the following solution handle all of them correctly?
                If not, what specific changes are needed?
                Be extremely thorough - this is the final quality gate.
                """,
                context=solution
            )
            for solution in revised_solutions
        ]
        validations = await asyncio.gather(*validation_tasks)

        # Final revision based on edge case validation
        final_revision_tasks = [
            self.revise(
                instruction=f"""
                Final revision based on edge case validation:
                {validation}
                
                Make any final adjustments to ensure robustness.
                This is the last chance to fix issues before final submission.
                Ensure the solution is clean, correct, and handles all edge cases.
                """,
                context=solution
            )
            for solution, validation in zip(revised_solutions, validations)
        ]
        final_solutions = await asyncio.gather(*final_revision_tasks)

        # Phase 5: Ensemble - Select or synthesize the best solution
        final_answer = await self.ensemble(
            instruction="""
            Select the best solution from the candidates below, or synthesize a new one
            combining the strongest elements of each. Criteria:
            1. Correctness (handles all examples and edge cases)
            2. Clarity (easy to understand and maintain)
            3. Completeness (handles all requirements from specification)
            4. Robustness (no obvious bugs or edge case failures)
            5. Conciseness (no unnecessary complexity)
            
            If synthesizing, clearly indicate which parts came from which solution.
            The final output should be ready for submission - clean, correct, and complete.
            """,
            contexts_list=final_solutions
        )

        return final_answer