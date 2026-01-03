# Workflow ID: mbppplus_14_0
# Benchmark: mbppplus
# Data Indices: [349, 153]

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

        # Step 1: Meta-classification - Understand problem nature via parallel perspectives
        classification_tasks = [
            self.generate(
                instruction="""Analyze the problem from a computational perspective:
                - Identify whether this is primarily a mathematical, structural, or logical problem
                - Determine if it requires iteration, recursion, formulaic calculation, or pattern matching
                - Note any explicit or implicit constraints mentioned
                - Predict likely edge cases (empty inputs, single elements, type boundaries)
                - Suggest 2-3 high-level solution strategies
                Format your response as a structured JSON-like outline.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from a data structure and type perspective:
                - What are the input types? (lists, tuples, integers, strings, etc.)
                - What is the expected output type and format?
                - Are there type conversion or coercion requirements?
                - What structural operations are implied? (indexing, zipping, filtering, mapping)
                - Identify any potential type-related edge cases
                Format your response as a structured JSON-like outline.""",
                context=""
            )
        ]
        
        classification_results = await asyncio.gather(*classification_tasks)
        
        # Step 2: Ensemble classifications into unified problem profile
        problem_profile = await self.ensemble(
            instruction="""Synthesize the two classification perspectives into a unified problem profile:
            - Combine computational and data structure insights
            - Resolve any contradictions between the two analyses
            - Prioritize solution strategies based on problem constraints
            - Explicitly state the most suitable approach (formulaic, iterative, recursive, etc.)
            - Highlight critical edge cases that must be handled
            - Output a concise, actionable problem-solving blueprint.""",
            contexts_list=classification_results
        )

        # Step 3: Conditional decomposition - only if problem is structural/complex
        decomposition_needed = await self.generate(
            instruction=f"""Based on this problem profile:
            {problem_profile}
            
            Determine if this problem requires explicit decomposition into subproblems.
            Answer only 'YES' or 'NO'.""",
            context=problem_profile
        )

        subproblems = []
        if "YES" in decomposition_needed.upper():
            subproblems_raw = await self.decompose(
                instruction=f"""Decompose this problem based on the following profile:
                {problem_profile}
                
                Break it down into minimal, executable subproblems with clear dependencies.
                Each subproblem should be solvable independently or in sequence.
                Focus on edge case handling, type validation, and core logic separation.""",
                context=problem_profile
            )
            # Summarize subproblems for cleaner context
            subproblems_summary = await self.summarize(
                instruction="Convert the subproblem list into a concise, numbered action plan.",
                context=str(subproblems_raw)
            )
            subproblems = [subproblems_summary]
        else:
            subproblems = [problem_profile]

        # Step 4: Generate initial solution candidates in parallel
        solution_candidates = await asyncio.gather(
            self.programmer(
                instruction=f"""Implement the solution based on this problem profile:
                {problem_profile}
                
                Requirements:
                - Use the exact function signature specified in the problem
                - Handle all identified edge cases explicitly
                - Include type validation and guard clauses
                - Return the correct data type (list, tuple, string, etc.)
                - Prioritize correctness over performance, but avoid obvious inefficiencies
                - Write clean, readable code with meaningful variable names""",
                context=subproblems[0]
            ),
            self.generate(
                instruction=f"""Generate a natural language solution strategy based on:
                {problem_profile}
                
                Then translate it into pseudocode that could be implemented in Python.
                Focus on algorithmic clarity and edge case handling.
                This will be used as an alternative solution path.""",
                context=subproblems[0]
            )
        )

        # Step 5: Adversarial validation loop (up to 3 iterations)
        current_solution = solution_candidates[0]
        for iteration in range(3):
            # Generate edge case tests and validation critique
            validator_prompt = f"""Critically evaluate this solution:
            {current_solution}
            
            Generate 5-7 edge case test scenarios that could break this solution.
            Common edge cases include: empty inputs, single elements, duplicates, type mismatches, 
            boundary values, and performance stress tests.
            
            For each edge case, explain why it might fail and how to fix it.
            If no flaws are found, state "VALIDATED".
            Format as numbered list with clear failure analysis."""
            
            validation_result = await self.generate(
                instruction=validator_prompt,
                context=current_solution
            )
            
            if "VALIDATED" in validation_result.upper():
                break
            else:
                # Revise solution based on validation feedback
                current_solution = await self.revise(
                    instruction=f"""Improve the solution based on this validation feedback:
                    {validation_result}
                    
                    Requirements:
                    - Fix all identified edge case vulnerabilities
                    - Maintain original function signature
                    - Preserve core logic while adding robustness
                    - Add explicit error handling or guard clauses where needed
                    - Ensure type consistency in all return paths""",
                    context=current_solution
                )

        # Step 6: Final ensemble - combine best elements if multiple candidates exist
        final_candidates = [current_solution]
        if len(solution_candidates) > 1:
            # Convert pseudocode to actual code if it looks promising
            pseudocode_implementation = await self.programmer(
                instruction=f"""Convert this pseudocode solution into working Python code:
                {solution_candidates[1]}
                
                Requirements:
                - Match the exact function signature from the original problem
                - Handle all edge cases mentioned in the problem profile
                - Return correct data types
                - Include necessary imports
                - Write production-ready code""",
                context=solution_candidates[1]
            )
            final_candidates.append(pseudocode_implementation)

        # Ensemble final solutions
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below:
            - Prioritize correctness and edge case handling above all else
            - Second priority: code clarity and readability
            - Third priority: efficiency and conciseness
            - Ensure the solution matches the exact function signature required
            - Verify that all imports are included and types are handled properly
            - The final output should be ONLY the Python function implementation, nothing else""",
            contexts_list=final_candidates
        )

        return final_solution