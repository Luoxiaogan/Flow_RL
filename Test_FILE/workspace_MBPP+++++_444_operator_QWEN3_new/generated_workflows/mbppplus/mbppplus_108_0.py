# Workflow ID: mbppplus_108_0
# Benchmark: mbppplus
# Data Indices: [181, 192, 5]

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
        import json

        # PHASE 1: Problem Classification
        classification = await self.generate(
            instruction="""Perform deep problem classification. Analyze:
            1. Primary category: mathematical, algorithmic, data transformation, search, or logical validation
            2. Required computational pattern: direct formula, iteration, recursion, binary search, combinatorial, etc.
            3. Input/output types: lists, tuples, numbers, strings, sets
            4. Critical constraints: order preservation, duplicates handling, empty input behavior, performance bounds
            5. Edge cases: minimum/maximum values, empty structures, single elements, boundary conditions
            6. Confidence level: high/medium/low in classification
            Output as structured JSON with keys: category, pattern, input_type, output_type, constraints, edge_cases, confidence""",
            context=""
        )

        # PHASE 2: Constraint Extraction
        constraints = await self.generate(
            instruction=f"""Extract explicit and implicit constraints from problem:
            - Input validation requirements
            - Output format and type specifications
            - Performance or complexity expectations
            - Mutability constraints (modify input or not)
            - Error handling expectations
            - All identified edge cases from classification: {classification}
            Format as bullet-point list with clear, actionable constraints""",
            context=classification
        )

        # PHASE 3: Parallel Solution Generation
        solution_strategies = [
            "Implement using direct mathematical derivation or formula",
            "Implement using iterative algorithm with index manipulation",
            "Implement using optimized data structure or search pattern",
            "Implement using functional or declarative approach"
        ]

        solution_attempts = await asyncio.gather(*[
            self.generate(
                instruction=f"""Generate complete function implementation.
                Classification context: {classification}
                Constraints: {constraints}
                Strategy: {strategy}
                Requirements:
                - Match exact function signature from problem
                - Handle all edge cases explicitly
                - Return correct data type
                - Include necessary imports inside function if needed
                - No outer wrappers or classes
                - Code must be production-ready and pass rigorous testing
                Output ONLY the function code, nothing else.""",
                context=""
            ) for strategy in solution_strategies
        ])

        # PHASE 4: Parallel Validation & Refinement
        refined_solutions = []
        for attempt in solution_attempts:
            # First revision: fix obvious errors and edge cases
            refined = await self.revise(
                instruction=f"""Critically revise this solution:
                - Check for off-by-one errors
                - Validate empty input handling
                - Confirm type consistency (list vs tuple vs set)
                - Verify against sample test cases if available
                - Ensure no input mutation
                - Optimize for clarity and correctness
                - Add comments only if they clarify non-obvious logic
                Constraints: {constraints}
                Classification: {classification}""",
                context=attempt
            )
            # Second revision: deeper validation
            deeply_refined = await self.revise(
                instruction="""Final validation pass:
                - Does this solution handle ALL edge cases?
                - Is the return type exactly as specified?
                - Are there any logical gaps or unhandled conditions?
                - Would this pass 100+ hidden test cases including extremes?
                If any doubt, fix it. Output only the corrected function code.""",
                context=refined
            )
            refined_solutions.append(deeply_refined)

        # PHASE 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Select and synthesize the best solution:
            Criteria:
            1. Correctness: handles all edge cases and constraints
            2. Robustness: no assumptions about input validity
            3. Efficiency: appropriate algorithmic complexity
            4. Readability: clear variable names and logical flow
            5. Type safety: exact match to expected return type
            If multiple solutions are equally valid, combine their strongest elements.
            Output ONLY the final function implementation, nothing else.""",
            contexts_list=refined_solutions
        )

        # PHASE 6: Final Sanity Check
        sanity_check = await self.generate(
            instruction=f"""Final verification:
            Does this solution:
            - Match the exact function signature?
            - Handle empty inputs?
            - Return correct data type?
            - Pass the sample test cases (if any provided)?
            - Contain no debugging code or print statements?
            If any issue found, return 'REJECT' followed by issue description.
            Otherwise, return 'ACCEPT'.
            Solution to verify: {final_solution}""",
            context=final_solution
        )

        # Conditional: if rejected, attempt one more refinement
        if "REJECT" in sanity_check:
            final_solution = await self.revise(
                instruction=f"""Critical fix required:
                Issues found: {sanity_check}
                Constraints: {constraints}
                Classification: {classification}
                Fix ALL identified issues. Output only the corrected function code.""",
                context=final_solution
            )

        return final_solution