# Workflow ID: mgsmbn_69_0
# Benchmark: mgsmbn
# Data Indices: [65]

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

        # Step 1: Parallel problem analysis - extract entities & classify problem type
        entity_extraction_task = self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract all mathematical entities, relationships, and constraints. Structure your output as follows:
            - Entities: List all objects, people, or quantities mentioned (e.g., 'football team', 'games won', 'games lost')
            - Known Values: List all explicitly given numbers with their meanings (e.g., 'total games = 22')
            - Unknowns: List what needs to be solved for (e.g., 'number of games won = ?')
            - Relationships: Describe all mathematical relationships in equation form if possible (e.g., 'wins = losses + 8')
            - Constraints: Note any implicit constraints (e.g., 'all values must be non-negative integers')
            - Problem Type: Classify as one of: algebraic, proportional, sequential, comparative, or distribution.
            Be meticulous and double-check your extraction against the original problem.""",
            context=""
        )

        decomposition_task = self.decompose(
            instruction="""Break down this mathematical word problem into a sequence of solvable subproblems. For each subproblem:
            - Clearly state what needs to be calculated or determined
            - Specify any dependencies (which subproblems must be solved first)
            - Indicate the type of operation needed (algebraic manipulation, arithmetic calculation, logical deduction, etc.)
            - Note any intermediate variables that need to be introduced
            Structure the output as a numbered list of subproblems with dependencies clearly marked.""",
            context=""
        )

        # Execute both tasks in parallel
        entity_analysis, decomposition = await asyncio.gather(entity_extraction_task, decomposition_task)

        # Step 2: Ensemble the analyses into a unified problem model
        unified_model = await self.ensemble(
            instruction="""Synthesize the entity extraction and problem decomposition into a single coherent problem-solving plan. Your output should include:
            1. A clear restatement of the problem in mathematical terms
            2. A prioritized list of subproblems to solve, with dependencies
            3. The overall strategy for solving (e.g., 'Set up system of equations and solve algebraically')
            4. Any potential pitfalls or ambiguities to watch for
            5. Expected format of the final answer (integer, decimal, etc.)
            Ensure consistency between the extracted entities and the decomposition steps.""",
            contexts_list=[entity_analysis, decomposition]
        )

        # Step 3: Iteratively solve each subproblem with validation
        subproblem_solutions = {}
        decomposition_list = await self.decompose(
            instruction="""Parse the following problem decomposition and return it as a structured list of subproblems with IDs and dependencies. Each item should have:
            - id: A unique identifier (e.g., 'SP1', 'SP2')
            - description: Clear description of what to solve
            - dependencies: Comma-separated list of prerequisite subproblem IDs (or 'none' if none)
            Format as a JSON-like list of dictionaries.""",
            context=decomposition
        )

        # Solve subproblems in dependency order
        for subproblem in decomposition_list:
            subproblem_id = subproblem['id']
            description = subproblem['description']
            dependencies = subproblem['dependencies'].split(',') if subproblem['dependencies'] != 'none' else []

            # Wait for dependencies to be solved
            dependency_context = "\n".join([f"{dep}: {subproblem_solutions[dep]}" for dep in dependencies if dep in subproblem_solutions])

            # Generate solution attempt
            solution_attempt = await self.generate(
                instruction=f"""Solve the following subproblem as part of a larger mathematical word problem:
                Subproblem: {description}
                Dependencies (already solved): {dependency_context if dependency_context else 'None'}
                Unified Problem Model: {unified_model}
                
                Provide your solution as a single numerical value or a clear mathematical expression. Show your reasoning step by step, but ensure the final answer is unambiguous. If you need to perform calculations, do them precisely and double-check your work.""",
                context=dependency_context
            )

            # Validate solution
            validation = await self.generate(
                instruction=f"""Critically validate the following subproblem solution:
                Subproblem: {description}
                Proposed Solution: {solution_attempt}
                Unified Problem Model: {unified_model}
                Dependency Solutions: {dependency_context}
                
                Check for:
                - Mathematical correctness
                - Consistency with dependencies
                - Adherence to constraints (e.g., non-negative, integer if required)
                - Unit consistency (if applicable)
                If valid, respond with 'VALID: [solution]'. If invalid, respond with 'INVALID: [detailed reason]'.""",
                context=solution_attempt
            )

            # If invalid, attempt revision (max 2 retries)
            retries = 0
            while "INVALID" in validation and retries < 2:
                solution_attempt = await self.revise(
                    instruction=f"""Revise the solution based on this validation feedback:
                    Validation Feedback: {validation}
                    Subproblem: {description}
                    Dependencies: {dependency_context}
                    Unified Model: {unified_model}
                    
                    Correct any errors and provide a revised solution. Be more careful with calculations and constraints this time.""",
                    context=solution_attempt
                )
                validation = await self.generate(
                    instruction=f"""Re-validate the revised solution:
                    Subproblem: {description}
                    Revised Solution: {solution_attempt}
                    Unified Problem Model: {unified_model}
                    Dependency Solutions: {dependency_context}
                    
                    Check for mathematical correctness and consistency. Respond with 'VALID: [solution]' or 'INVALID: [reason]'.""",
                    context=solution_attempt
                )
                retries += 1

            # Extract final solution (even if still marked invalid, proceed with best attempt)
            if "VALID:" in validation:
                final_solution = validation.split("VALID:")[1].strip()
            else:
                # Fallback: extract any number from the solution attempt
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", solution_attempt)
                final_solution = numbers[0] if numbers else "0"

            subproblem_solutions[subproblem_id] = final_solution

        # Step 4: Synthesize final answer from subproblem solutions
        final_answer_attempt = await self.generate(
            instruction=f"""Using the solved subproblems, compute the final answer to the original question.
            Subproblem Solutions: {subproblem_solutions}
            Unified Problem Model: {unified_model}
            
            Show the final calculation step that leads to the answer. The answer must be a single numerical value (integer or decimal) with no units or additional text. Double-check that this matches what was asked in the original problem.""",
            context=str(subproblem_solutions)
        )

        # Step 5: Use Programmer for precise computation if needed
        # Extract any mathematical expression from the final answer attempt
        programmer_result = await self.programmer(
            instruction=f"""Extract any mathematical expression or calculation from the following text and compute it precisely. Return only the numerical result, nothing else.
            If no calculation is needed and a number is already provided, return that number.
            Text: {final_answer_attempt}""",
            context=final_answer_attempt,
            max_retries=3
        )

        # Step 6: Sanitize output to ensure it's a clean number
        sanitized_answer = await self.revise(
            instruction="""Extract only the numerical value from the following text. Remove any units, explanations, or formatting. The output must be a single number (integer or decimal) and nothing else.
            Examples:
            Input: "The answer is 15 games" → Output: "15"
            Input: "23.5 taka" → Output: "23.5"
            Input: "x = 42" → Output: "42"
            Be strict - only return the number.""",
            context=programmer_result
        )

        # Final extraction of number using regex as safety net
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", sanitized_answer)
        final_answer = numbers[0] if numbers else "0"

        return final_answer