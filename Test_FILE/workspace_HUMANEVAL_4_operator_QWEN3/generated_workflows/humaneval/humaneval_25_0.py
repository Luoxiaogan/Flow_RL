# Workflow ID: humaneval_25_0
# Benchmark: humaneval
# Data Indices: [89, 19]

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
        
        # PHASE 1: Pattern Extraction and Refinement
        pattern_analysis = await self.generate(
            instruction="""Analyze the provided examples in the docstring with forensic precision.
            For each example, compare input and output to reverse-engineer the transformation rule.
            Identify:
            - The type of operation (string manipulation, mathematical, sorting, etc.)
            - The exact mapping or formula applied
            - Edge cases (empty input, single characters, boundary values)
            - Return type requirements (int vs float, string format)
            - Any implicit constraints (case sensitivity, character sets, etc.)
            Present your analysis as a structured hypothesis that could be directly implemented in code.""",
            context=""
        )
        
        refined_pattern = await self.revise(
            instruction="""Critically examine the transformation hypothesis.
            - Are there inconsistencies between examples?
            - Are edge cases properly handled?
            - Is the return type precisely matched?
            - Could there be hidden constraints not shown in examples?
            - Is the solution minimal (no over-engineering)?
            Refine the hypothesis to be watertight, explicit, and directly implementable.
            If any ambiguity remains, state your conservative assumption.""",
            context=pattern_analysis
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Implement the solution using an IMPERATIVE approach (for loops, conditionals, mutable state).
                Context: {refined_pattern}
                Requirements:
                - Function name must exactly match ENTRY POINT
                - Return type must match examples precisely
                - Handle all edge cases mentioned in analysis
                - No imports unless absolutely necessary (will be auto-added)
                - Code must be minimal and direct
                Return ONLY the function definition with no additional text.""",
                context=refined_pattern
            ),
            self.generate(
                instruction=f"""Implement the solution using a FUNCTIONAL approach (list comprehensions, map/filter, recursion).
                Context: {refined_pattern}
                Requirements:
                - Function name must exactly match ENTRY POINT
                - Return type must match examples precisely
                - Handle all edge cases mentioned in analysis
                - No imports unless absolutely necessary (will be auto-added)
                - Code must be minimal and direct
                Return ONLY the function definition with no additional text.""",
                context=refined_pattern
            ),
            self.generate(
                instruction=f"""Implement the solution using a MATHEMATICAL/FORMULA approach (arithmetic, modular operations, precomputed tables).
                Context: {refined_pattern}
                Requirements:
                - Function name must exactly match ENTRY POINT
                - Return type must match examples precisely
                - Handle all edge cases mentioned in analysis
                - No imports unless absolutely necessary (will be auto-added)
                - Code must be minimal and direct
                Return ONLY the function definition with no additional text.""",
                context=refined_pattern
            )
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Ensemble Selection with Validation
        selected_solution = await self.ensemble(
            instruction="""Evaluate all candidate solutions against these criteria:
            1. Correctness: Would it pass all provided examples? Mentally simulate each.
            2. Precision: Does it match return types exactly (int vs float, string format)?
            3. Completeness: Does it handle edge cases from the analysis?
            4. Minimalism: Is it free of unnecessary complexity or imports?
            5. Naming: Does the function name exactly match ENTRY POINT?
            Select the best solution. If multiple are equally good, choose the most readable.
            If all have flaws, select the one with the fewest and most fixable issues.
            Return ONLY the selected function code with no additional text.""",
            contexts_list=strategy_solutions
        )

        # PHASE 4: Iterative Refinement Loop (up to 3 iterations)
        current_solution = selected_solution
        for iteration in range(3):
            critique = await self.generate(
                instruction=f"""Critically evaluate this solution for hidden flaws:
                {current_solution}
                
                Check:
                - Does it handle empty inputs?
                - Does it preserve data types exactly?
                - Are there off-by-one errors?
                - Does it match the transformation rule precisely?
                - Is the function name exactly correct?
                - Are there any assumptions not supported by examples?
                If no flaws found, respond with "VALID: Fully matches specification."
                Otherwise, list specific, actionable fixes needed.""",
                context=current_solution
            )
            
            if "VALID:" in critique or "fully matches" in critique.lower():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix the identified issues in this solution:
                Critique: {critique}
                
                Requirements:
                - Maintain exact function name
                - Preserve return type precision
                - Address all critique points
                - Keep code minimal
                Return ONLY the revised function code with no additional text.""",
                context=current_solution
            )

        return current_solution