# Workflow ID: mbppplus_63_0
# Benchmark: mbppplus
# Data Indices: [222, 1, 67]

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

        # Phase 1: Decompose the problem
        decomposition = await self.generate(
            instruction="""Perform a deep structural decomposition of this programming problem. Identify:
            1. Input types and constraints (string, list, number, etc.)
            2. Expected output type and format (must match test cases exactly)
            3. Problem category (string manipulation, mathematical, logical, etc.)
            4. Key operations needed (searching, replacing, comparing, etc.)
            5. Critical edge cases (empty input, single element, duplicates, boundaries)
            6. Reference solution approach if visible (but don't copy it)
            7. Potential failure modes or common mistakes
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel strategy generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this problem decomposition:
                {decomposition}
                
                Generate a complete, production-ready Python function solution.
                Strategy 1: Use regex-based approaches where applicable.
                - Include necessary imports inside the function
                - Handle all edge cases mentioned in decomposition
                - Match exact return types from test cases
                - Write clean, readable code with meaningful variable names
                Return ONLY the function implementation, nothing else.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Based on this problem decomposition:
                {decomposition}
                
                Generate a complete, production-ready Python function solution.
                Strategy 2: Use native Python methods and manual iteration.
                - Avoid regex unless absolutely necessary
                - Include necessary imports inside the function
                - Handle all edge cases mentioned in decomposition
                - Match exact return types from test cases
                - Optimize for clarity and maintainability
                Return ONLY the function implementation, nothing else.""",
                context=decomposition
            )
        ]

        # Generate additional strategy if problem seems mathematical
        if any(keyword in decomposition.lower() for keyword in ["math", "number", "sequence", "arithmetic"]):
            strategy_tasks.append(
                self.generate(
                    instruction=f"""Based on this problem decomposition:
                    {decomposition}
                    
                    Generate a complete, production-ready Python function solution.
                    Strategy 3: Mathematical/algorithmic approach with formula derivation.
                    - Focus on computational efficiency
                    - Include mathematical reasoning in comments if needed
                    - Handle edge cases like zero, negative numbers, overflow
                    - Match exact return types from test cases
                    Return ONLY the function implementation, nothing else.""",
                    context=decomposition
                )
            )

        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # Phase 3: Ensemble the best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the candidates below.
            Criteria:
            1. Correctness: Must handle all edge cases identified in decomposition
            2. Robustness: Should work for all test cases, not just examples
            3. Efficiency: Prefer simpler, faster approaches when equivalent
            4. Readability: Clean code with good variable names
            5. Type safety: Exact return type matching test cases
            6. Import handling: All imports inside function, only when needed
            
            Take the strongest elements from each solution. If one solution is clearly superior, select it.
            Return ONLY the final function implementation, nothing else.""",
            contexts_list=strategy_solutions
        )

        # Phase 4: Validation and refinement loop
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {final_solution}
                
                Against this problem decomposition:
                {decomposition}
                
                Check for:
                1. Edge case handling (empty inputs, single elements, boundaries)
                2. Return type consistency (tuple vs list vs string vs None)
                3. Logic errors or off-by-one mistakes
                4. Missing imports or incorrect scoping
                5. Performance issues or unnecessary complexity
                6. Deviation from test case expectations
                
                If any issues found, describe them specifically. If perfect, say "VALIDATED".
                Return either "VALIDATED" or a detailed list of issues to fix.""",
                context=final_solution
            )

            if "VALIDATED" in validation.upper():
                break

            # Revise based on validation feedback
            final_solution = await self.revise(
                instruction=f"""Revise this solution to fix the following issues:
                {validation}
                
                Original problem decomposition:
                {decomposition}
                
                Requirements:
                - Maintain exact function signature
                - Keep all imports inside function
                - Preserve handling of previously correct cases
                - Return ONLY the revised function implementation, nothing else.""",
                context=final_solution
            )

        return final_solution