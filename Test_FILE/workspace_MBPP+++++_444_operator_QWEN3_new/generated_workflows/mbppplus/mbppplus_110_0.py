# Workflow ID: mbppplus_110_0
# Benchmark: mbppplus
# Data Indices: [293, 60, 177]

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

        # Step 1: Problem Decomposition - Extract core requirements, input/output specs, edge cases
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the programming problem to extract:
            1. Input format and data types (e.g., string, list of numbers, mixed types)
            2. Expected output format and data types (e.g., tuple, list, single value)
            3. Core transformation logic (what operation must be performed?)
            4. Edge cases to consider (empty inputs, single elements, duplicates, boundary values)
            5. Any implicit constraints (order preservation, type consistency, performance)
            6. Function signature requirements (exact parameter names and return type)
            
            Structure your response as:
            INPUT: [description]
            OUTPUT: [description]
            LOGIC: [description]
            EDGE_CASES: [list]
            CONSTRAINTS: [list]
            SIGNATURE: [exact function name and parameters]""",
            context=""
        )

        # Step 2: Generate multiple solution hypotheses in parallel
        hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focused on CORRECTNESS and EDGE CASES.
                Use the problem decomposition:
                {decomposition}
                
                Prioritize:
                - Handling all edge cases mentioned in decomposition
                - Exact return type matching (tuple vs list vs set)
                - Defensive programming (validate inputs if needed)
                - Clear, readable code with comments for complex logic
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focused on PERFORMANCE and EFFICIENCY.
                Use the problem decomposition:
                {decomposition}
                
                Prioritize:
                - Algorithmic efficiency (avoid unnecessary operations)
                - Minimal memory usage
                - Built-in functions and libraries where appropriate
                - Clean, idiomatic Python
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focused on ROBUSTNESS and TYPE SAFETY.
                Use the problem decomposition:
                {decomposition}
                
                Prioritize:
                - Strict type handling (convert and validate types explicitly)
                - Error handling for malformed inputs (if applicable)
                - Comprehensive edge case coverage
                - Defensive checks and assertions (if appropriate)
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            )
        )

        # Step 3: Critique and refine each hypothesis
        refined_hypotheses = []
        for i, hypothesis in enumerate(hypotheses):
            focus = ["correctness", "performance", "robustness"][i]
            refined = await self.revise(
                instruction=f"""Critically review this solution for {focus}:
                {hypothesis}
                
                Check against problem decomposition:
                {decomposition}
                
                Specifically verify:
                1. Does it handle all edge cases listed in EDGE_CASES?
                2. Does it return the exact data type specified in OUTPUT?
                3. Does it preserve the function signature from SIGNATURE?
                4. Are there any logical errors or off-by-one mistakes?
                5. Is the code clean and readable?
                
                Fix any issues found. Return ONLY the corrected function implementation with necessary imports, nothing else.""",
                context=hypothesis
            )
            refined_hypotheses.append(refined)

        # Step 4: Ensemble - Synthesize the best elements from all refined solutions
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the following candidates:
            Each solution has different strengths (correctness, performance, robustness).
            Create a final solution that:
            1. Is 100% correct for all edge cases
            2. Is as efficient as possible
            3. Is robust and type-safe
            4. Matches the exact function signature required
            5. Is clean and readable
            
            Choose the best approach for each part of the solution. If one solution is clearly superior, use it entirely.
            Return ONLY the final function implementation with necessary imports, nothing else.""",
            contexts_list=refined_hypotheses
        )

        # Step 5: Final validation and cleanup
        validated_solution = await self.revise(
            instruction=f"""Final validation pass:
            {final_solution}
            
            Ensure:
            1. Function name and parameters EXACTLY match: {re.search(r'SIGNATURE:\s*(.+)', decomposition).group(1) if re.search(r'SIGNATURE:\s*(.+)', decomposition) else 'unknown'}
            2. Return type matches OUTPUT specification from decomposition
            3. No extra text, comments, or explanations - ONLY the function implementation
            4. All necessary imports are included at the top
            5. Code is clean and follows Python best practices
            
            Return ONLY the validated function implementation, nothing else.""",
            context=final_solution
        )

        return validated_solution