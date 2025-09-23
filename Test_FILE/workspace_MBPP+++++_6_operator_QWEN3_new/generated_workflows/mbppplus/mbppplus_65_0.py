# Workflow ID: mbppplus_65_0
# Benchmark: mbppplus
# Data Indices: [188, 180]

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

        # Step 1: Classify problem and determine solution strategy
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Classify problem type: Is it mathematical, algorithmic, data structure, string manipulation, or logical?
            2. Identify required operations: Does it need iteration, recursion, formula application, or set operations?
            3. Anticipate edge cases: What are the boundary conditions? (empty inputs, zero, negative numbers, duplicates, etc.)
            4. Suggest solution strategy: What approach is most appropriate? (direct computation, brute force, optimized algorithm, etc.)
            5. Note any constraints: Time complexity, space complexity, or specific output format requirements.
            Provide comprehensive analysis in structured paragraphs.""",
            context=""
        )

        # Step 2: Generate multiple solution candidates in parallel
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete Python solution that:
                - Uses the EXACT function signature from the problem
                - Includes all necessary imports INSIDE the function
                - Handles edge cases explicitly
                - Returns the correct data type
                - Is clean, readable, and efficient
                Focus on mathematical elegance and simplicity.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete Python solution that:
                - Uses the EXACT function signature from the problem
                - Includes all necessary imports INSIDE the function
                - Handles edge cases explicitly with defensive programming
                - Returns the correct data type
                - Prioritizes robustness over elegance
                Include detailed comments explaining edge case handling.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete Python solution that:
                - Uses the EXACT function signature from the problem
                - Includes all necessary imports INSIDE the function
                - Follows best practices for the identified problem type
                - Returns the correct data type
                - Is optimized for performance within reason
                Reference common algorithms or patterns for this problem type.""",
                context=classification
            )
        )

        # Step 3: Validate each candidate solution
        validation_reports = await asyncio.gather(
            *[self.programmer(
                instruction="""Critically analyze this code solution:
                1. Does it match the required function signature exactly?
                2. Are all imports correctly placed inside the function?
                3. Does it handle all anticipated edge cases from the classification?
                4. Is the return type correct?
                5. Are there any logical errors or potential bugs?
                6. Is the code clean and readable?
                Provide detailed critique with specific improvement suggestions.""",
                context=candidate
            ) for candidate in solution_candidates]
        )

        # Step 4: Revise each solution based on validation
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve this solution based on the validation report:
                Validation: {report}
                
                Fix all identified issues while preserving the core approach.
                Ensure:
                - Correct function signature
                - Proper import placement
                - Edge case handling
                - Correct return type
                - Clean, readable code
                If the solution is fundamentally flawed, completely rewrite it following the same general strategy.""",
                context=solution_candidates[i]
            ) for i, report in enumerate(validation_reports)]
        )

        # Step 5: Ensemble - select best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from these candidates:
            Criteria:
            1. Correctness: Must handle all edge cases and produce correct output
            2. Simplicity: Prefer elegant, straightforward solutions
            3. Robustness: Must include proper error handling and edge case management
            4. Format: Must follow exact output requirements (function signature, imports inside function, etc.)
            5. Readability: Code should be clean and well-structured
            If multiple solutions are equally good, choose the most readable.
            If all solutions have critical flaws, respond with 'ALL_SOLUTIONS_FLAWED'""",
            contexts_list=revised_solutions
        )

        # Step 6: Fallback decomposition if all solutions flawed
        if "ALL_SOLUTIONS_FLAWED" in final_solution:
            decomposition = await self.decompose(
                instruction="""Break this problem into fundamental subproblems:
                1. Identify core mathematical or logical operations needed
                2. Define input validation requirements
                3. Specify edge case handling procedures
                4. Outline step-by-step solution process
                Return as numbered subproblems with dependencies.""",
                context=classification
            )
            
            # Solve each subproblem
            subproblem_solutions = []
            for subproblem in decomposition:
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Based on the overall problem classification:
                    {classification}
                    
                    Provide only the code or logic needed for this specific subproblem.""",
                    context=classification
                )
                subproblem_solutions.append(sub_solution)
            
            # Synthesize final solution from subproblems
            final_solution = await self.generate(
                instruction=f"""Synthesize a complete solution from these subproblem solutions:
                {chr(10).join(subproblem_solutions)}
                
                Create a complete Python function that:
                - Uses the EXACT function signature from the problem
                - Includes all necessary imports INSIDE the function
                - Integrates all subproblem solutions coherently
                - Handles edge cases
                - Returns correct data type
                - Is clean and readable""",
                context=classification
            )

        # Step 7: Final validation and cleanup
        final_validation = await self.generate(
            instruction="""Verify this final solution meets all requirements:
            1. EXACT function signature match
            2. All imports inside function
            3. Proper edge case handling
            4. Correct return type
            5. Clean, readable code
            6. No extraneous text or explanations
            If any requirement is violated, fix it immediately.
            Return ONLY the corrected Python code with no additional text.""",
            context=final_solution
        )

        return final_validation