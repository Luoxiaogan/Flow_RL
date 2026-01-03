# Workflow ID: mbppplus_92_0
# Benchmark: mbppplus
# Data Indices: [147, 306]

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

        # STEP 1: CLASSIFY PROBLEM TYPE AND STRATEGY
        classification = await self.generate(
            instruction="""Analyze this programming problem deeply and classify it by:
            1. Primary domain: string manipulation, mathematical sequence, list/set operation, or logical validation.
            2. Solution approach: regex pattern, iterative algorithm, recursive logic, set operation, or direct computation.
            3. Key constraints: return type (list/tuple/set/string), order preservation, edge cases (empty, single element, duplicates).
            4. Required libraries: does it need re, math, itertools, or none?
            5. Complexity level: simple (direct), medium (multi-step), complex (stateful iteration).
            Output a structured classification with clear labels for each category.""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING BASED ON COMPLEXITY
        if "complex" in classification.lower() or "medium" in classification.lower():
            # Decompose into subproblems for complex/medium problems
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal, executable subproblems.
                Each subproblem must be:
                - Independently describable
                - Logically sequenced (respect dependencies)
                - Implementable as a code step
                - Include edge case handling as a separate subproblem if needed
                Return list of subproblems with dependencies.""",
                context=classification
            )
            
            # Execute subproblems sequentially respecting dependencies
            solution_context = classification
            for sub in subproblems:
                sub_desc = sub['description']
                sub_step = await self.generate(
                    instruction=f"""Generate Python code snippet for this subproblem:
                    {sub_desc}
                    Context from previous steps:
                    {solution_context}
                    Ensure type consistency and edge case handling.""",
                    context=solution_context
                )
                solution_context += f"\n\n# Subproblem: {sub_desc}\n{sub_step}"
            
            # Generate final integrated solution
            draft_solution = await self.programmer(
                instruction=f"""Synthesize a complete, runnable Python function from these subproblem solutions:
                {solution_context}
                Ensure function signature matches exactly. Handle all edge cases. Return correct type.
                Include necessary imports at top of function body if needed.""",
                context=solution_context,
                max_retries=2
            )
        else:
            # Simple problems: generate parallel solution candidates
            candidates = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate a direct, efficient Python solution.
                    Classification context: {classification}
                    Prioritize readability and correctness. Handle edge cases explicitly.
                    Return only the function implementation with necessary imports inside.""",
                    context=classification
                ),
                self.programmer(
                    instruction=f"""Generate an alternative Python solution using a different approach.
                    Classification context: {classification}
                    Example: if regex is obvious, try manual iteration. If math is direct, try algorithmic.
                    Still ensure correctness and edge case handling.""",
                    context=classification
                )
            )
            
            # Ensemble best solution
            draft_solution = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Correctness (handles edge cases, matches return type)
                2. Simplicity (minimal logic, readable)
                3. Robustness (defensive coding, no assumptions)
                4. Efficiency (reasonable time/space complexity)
                If both are good, synthesize a hybrid that combines their strengths.
                Return only the final function implementation.""",
                contexts_list=candidates
            )

        # STEP 3: SELF-CRITIQUE AND REVISION LOOP
        for iteration in range(2):  # Max 2 revision cycles
            critique = await self.generate(
                instruction=f"""Critique this solution for:
                - Edge cases: empty input, single element, boundary values, type mismatches
                - Return type: does it match exactly what's required (list vs tuple vs string)?
                - Imports: are they included inside the function if needed?
                - Efficiency: any obvious performance bottlenecks?
                - Readability: clear variable names, logical flow?
                Problem context: {classification}
                Current solution:
                {draft_solution}
                Output specific, actionable improvement points.""",
                context=draft_solution
            )
            
            # Check if critique found critical issues
            if "critical" in critique.lower() or "error" in critique.lower() or "fix" in critique.lower():
                draft_solution = await self.revise(
                    instruction=f"""Revise the solution to address these specific issues:
                    {critique}
                    Preserve correct parts. Only change what's necessary.
                    Maintain exact function signature and return type.
                    Return complete revised function implementation.""",
                    context=draft_solution
                )
            else:
                break  # No significant issues found

        # STEP 4: FINAL VALIDATION AND OUTPUT
        final_output = await self.revise(
            instruction="""Final polish:
            - Ensure ONLY the function implementation is returned (no explanations, no markdown)
            - Verify imports are inside the function if needed
            - Confirm function name and parameters match exactly
            - Remove any debug prints or comments unless essential
            - Format code cleanly with proper indentation
            Return the raw Python function code ready for execution.""",
            context=draft_solution
        )
        
        return final_output