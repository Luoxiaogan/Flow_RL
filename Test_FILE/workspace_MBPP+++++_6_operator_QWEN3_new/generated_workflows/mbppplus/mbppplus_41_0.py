# Workflow ID: mbppplus_41_0
# Benchmark: mbppplus
# Data Indices: [74, 311]

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

        # Step 1: Meta-classify the problem type and requirements
        problem_analysis = await self.generate(
            instruction="""Perform deep problem classification and strategy planning:
            1. Categorize the problem: Is it primarily mathematical, logical/conditional, data structure manipulation, or string processing?
            2. Identify required output type: scalar, list, tuple, set, or other?
            3. Detect critical edge cases: empty inputs, single elements, duplicates, negative numbers, boundary conditions?
            4. Suggest 2-3 potential solution approaches with their trade-offs (e.g., recursive vs iterative, set operations vs loops)
            5. Note any mathematical formulas, algorithms, or standard library functions that might be relevant
            6. Flag any potential precision, overflow, or type conversion issues
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Decompose into subproblems based on analysis
        decomposition = await self.decompose(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Decompose the problem into 2-5 atomic subproblems. For each:
            - Clearly state what needs to be computed or decided
            - Specify dependencies (which subproblems must be solved first)
            - Indicate whether it requires mathematical computation, logical branching, or data transformation
            Prioritize subproblems that handle edge cases or validation first.""",
            context=problem_analysis
        )

        # Step 3: Parallel solution generation - multiple approaches
        solution_approaches = [
            "Generate a mathematically rigorous solution focusing on algorithmic correctness and edge case handling",
            "Generate a practical, readable solution using Pythonic idioms and standard library functions",
            "Generate an optimized solution focusing on computational efficiency and minimal memory usage"
        ]
        
        solution_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""{approach_instruction}.
                Incorporate insights from problem analysis:
                {problem_analysis}
                
                Requirements:
                - Handle all identified edge cases
                - Match specified output type exactly
                - Include explanatory comments for complex logic
                - Use defensive programming practices
                - Return early for invalid inputs when appropriate""",
                context=""
            ) for approach_instruction in solution_approaches]
        )

        # Step 4: Generate code implementations for top candidates
        code_tasks = []
        for i, candidate in enumerate(solution_candidates[:2]):  # Focus on top 2 candidates
            code_task = self.programmer(
                instruction=f"""Implement this solution approach:
                {candidate}
                
                Based on problem analysis:
                {problem_analysis}
                
                Critical requirements:
                - Function signature must match exactly
                - Handle all edge cases identified in analysis
                - Return correct data type (list, tuple, scalar, etc.)
                - Include input validation where appropriate
                - Optimize for clarity first, then performance
                - Test with provided examples and edge cases""",
                context=candidate,
                max_retries=3
            )
            code_tasks.append(code_task)
        
        code_results = await asyncio.gather(*code_tasks)

        # Step 5: Adversarial revision - find flaws in generated solutions
        critique_tasks = []
        for code_result in code_results:
            critique = self.generate(
                instruction=f"""Play devil's advocate. Critically analyze this solution:
                {code_result}
                
                Look for:
                - Unhandled edge cases
                - Logical errors or off-by-one mistakes
                - Type mismatches or conversion issues
                - Performance bottlenecks
                - Violations of problem requirements
                - Potential integer overflow or precision loss
                Provide specific, actionable feedback for improvement.""",
                context=code_result
            )
            critique_tasks.append(critique)
        
        critiques = await asyncio.gather(*critique_tasks)

        # Step 6: Revise solutions based on critiques
        revised_solutions = []
        for i, (code_result, critique) in enumerate(zip(code_results, critiques)):
            if "critical flaw" in critique.lower() or "error" in critique.lower():
                revised = await self.revise(
                    instruction=f"""Fix all issues identified in critique:
                    {critique}
                    
                    Preserve the core approach but address all flaws.
                    Ensure solution handles all edge cases from original analysis.
                    Maintain correct function signature and return type.""",
                    context=code_result
                )
                revised_solutions.append(revised)
            else:
                revised_solutions.append(code_result)

        # Step 7: Ensemble - synthesize best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions:
            - Prioritize correctness and edge case handling above all
            - Choose the most readable and maintainable implementation
            - Incorporate performance optimizations where they don't compromise clarity
            - Ensure exact match with required function signature and return type
            - Include comprehensive comments explaining non-obvious logic
            - Verify solution against all identified edge cases
            Return only the final Python function implementation with imports if needed.""",
            contexts_list=revised_solutions
        )

        # Step 8: Final validation and cleanup
        cleaned_solution = await self.revise(
            instruction="""Final cleanup and validation:
            1. Ensure ONLY the function implementation is returned (no explanations, no markdown)
            2. Verify function signature matches exactly
            3. Confirm all necessary imports are included at top
            4. Remove any test code or print statements
            5. Ensure code is properly indented and formatted
            6. Double-check return types match requirements
            Return ONLY the clean Python code, nothing else.""",
            context=final_solution
        )

        return cleaned_solution