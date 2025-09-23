# Workflow ID: mbppplus_93_0
# Benchmark: mbppplus
# Data Indices: [139, 117]

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

        # Stage 1: Deep problem decomposition
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into fundamental components:
            1. Identify input type and structure (list, tuple, string, etc.)
            2. Identify expected output type and structure
            3. Determine the core transformation or algorithm required
            4. List all edge cases (empty inputs, single elements, boundary conditions)
            5. Note any implicit constraints from function signature or test cases
            6. Identify potential failure points in implementation
            Return structured subproblems with clear dependencies.""",
            context=""
        )

        # Convert decomposition to readable format for context
        decomposition_summary = "\n".join([
            f"Subproblem {item['id']}: {item['description']} (Depends on: {item['dependencies']})"
            for item in decomposition
        ])

        # Stage 2: Parallel solution hypothesis generation
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on the primary transformation logic:
                Problem decomposition: {decomposition_summary}
                - Implement the core algorithm shown in examples
                - Prioritize clarity and directness
                - Assume standard cases (non-empty, well-formed inputs)
                - Return only the function implementation with necessary imports""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on edge case handling:
                Problem decomposition: {decomposition_summary}
                - Handle all edge cases identified in decomposition
                - Include defensive programming practices
                - Consider type safety and boundary conditions
                - Return only the function implementation with necessary imports""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on performance and efficiency:
                Problem decomposition: {decomposition_summary}
                - Optimize for time/space complexity
                - Use most efficient Python constructs
                - Consider large input scenarios
                - Return only the function implementation with necessary imports""",
                context=""
            )
        )

        # Stage 3: Validation and synthesis
        validation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Critically validate this solution against problem requirements:
                Problem decomposition: {decomposition_summary}
                - Check input/output type consistency
                - Verify edge case handling
                - Confirm algorithm correctness
                - Identify any potential bugs or limitations
                - Rate solution on scale 1-10 for completeness""",
                context=solution
            ) for solution in solution_hypotheses]
        )

        # Ensemble selection with synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best aspects of all solutions:
            - Combine correct core logic with robust edge case handling
            - Prefer efficient implementations when correctness is equal
            - Ensure output matches exact type requirements from problem
            - Fix any identified bugs or limitations
            - Return ONLY the final function implementation with necessary imports
            - Do NOT include any explanatory text or comments""",
            contexts_list=solution_hypotheses
        )

        # Stage 4: Iterative refinement through execution
        for attempt in range(3):
            try:
                execution_result = await self.programmer(
                    instruction=f"""Execute this solution against comprehensive test cases:
                    Problem context: {decomposition_summary}
                    - Test with provided examples
                    - Test with edge cases from decomposition
                    - Test with boundary conditions
                    - Return execution results and any errors""",
                    context=final_solution,
                    max_retries=1
                )
                
                # Check if execution was successful
                if "error" not in execution_result.lower() and "exception" not in execution_result.lower():
                    break
                    
                # If errors, revise solution
                final_solution = await self.revise(
                    instruction=f"""Fix the following issues identified during execution:
                    Execution errors: {execution_result}
                    Problem decomposition: {decomposition_summary}
                    - Address specific errors mentioned
                    - Maintain correct function signature
                    - Preserve core algorithm while fixing bugs
                    - Return ONLY the revised function implementation""",
                    context=final_solution
                )
            except Exception as e:
                # If programmer fails, try one more revision
                if attempt < 2:
                    final_solution = await self.revise(
                        instruction=f"""Emergency fix for solution that failed to execute:
                        Error: {str(e)}
                        Problem decomposition: {decomposition_summary}
                        - Simplify implementation if necessary
                        - Focus on core functionality from examples
                        - Ensure basic test cases pass
                        - Return ONLY the function implementation""",
                        context=final_solution
                    )

        return final_solution