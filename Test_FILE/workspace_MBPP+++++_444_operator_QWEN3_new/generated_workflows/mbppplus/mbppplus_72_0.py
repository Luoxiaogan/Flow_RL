# Workflow ID: mbppplus_72_0
# Benchmark: mbppplus
# Data Indices: [324, 64, 224]

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

        # Step 1: Deep problem decomposition - extract core requirements
        decomposition = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem. Identify:
            1. Input data types and structures (list, tuple, set, etc.)
            2. Expected output type and format
            3. Core transformation logic required
            4. Edge cases that must be handled (empty inputs, single elements, duplicates, negatives, etc.)
            5. Any implicit constraints (order preservation, type consistency, mathematical domain)
            6. Failure modes that would cause incorrect behavior
            Present as structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Parallel solution generation - explore multiple approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this analysis:
                {decomposition}
                
                Generate Solution Approach 1: Mathematical/Reduction Focus
                - Treat problem as mathematical operation
                - Focus on arithmetic transformations
                - Handle edge cases explicitly
                - Return correct data type as specified
                - Include defensive checks for empty inputs
                Output ONLY the function implementation as specified in requirements.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {decomposition}
                
                Generate Solution Approach 2: Data Structure/Algorithmic Focus
                - Treat problem as data structure transformation
                - Use appropriate Python built-ins and methods
                - Preserve order if required, handle duplicates appropriately
                - Include explicit edge case handling
                - Return correct data type
                Output ONLY the function implementation as specified in requirements.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {decomposition}
                
                Generate Solution Approach 3: Functional/Declarative Focus
                - Use functional programming concepts (map, reduce, comprehensions)
                - Focus on declarative transformation
                - Handle edge cases through conditional logic
                - Ensure type consistency
                Output ONLY the function implementation as specified in requirements.""",
                context=decomposition
            )
        )

        # Step 3: Adversarial revision - try to break each solution
        stress_tested_solutions = []
        for i, solution in enumerate(solution_attempts):
            revised = await self.revise(
                instruction=f"""Adversarially critique and improve this solution:
                - Identify potential failure points (edge cases, type mismatches, off-by-one errors)
                - Test against empty inputs, single elements, duplicates, negatives, zeros
                - Verify return type matches requirements exactly
                - Ensure no unnecessary imports or complexity
                - If solution is already robust, return it unchanged
                - Output ONLY the improved function implementation""",
                context=solution
            )
            stress_tested_solutions.append(revised)

        # Step 4: Ensemble selection - choose the most robust solution
        final_solution = await self.ensemble(
            instruction="""Select the most robust, elegant, and correct solution from these candidates:
            - Prioritize solutions that explicitly handle edge cases
            - Favor solutions with clean, readable code
            - Ensure return type matches requirements exactly
            - Prefer solutions that use appropriate Python idioms
            - Eliminate any solutions with obvious flaws or type mismatches
            - If multiple solutions are equally good, choose the most concise
            Output ONLY the selected function implementation""",
            contexts_list=stress_tested_solutions
        )

        # Step 5: Final validation loop - try to break the chosen solution
        for attempt in range(3):  # Maximum 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Stress test this solution:
                {final_solution}
                
                Try to find inputs that would break this solution:
                - Empty inputs
                - Single element inputs
                - Extreme values (very large, very small, negative, zero)
                - Duplicate values
                - Type boundary cases
                If you find a breaking case, describe it specifically.
                If no breaking cases found, respond with 'VALIDATED'.""",
                context=final_solution
            )
            
            if "VALIDATED" in validation or "validated" in validation:
                break
            else:
                # Found potential issue - revise and continue
                final_solution = await self.revise(
                    instruction=f"""Improve this solution to handle the following failure case:
                    {validation}
                    
                    - Fix the identified issue while preserving existing functionality
                    - Maintain correct return type
                    - Keep code clean and efficient
                    - Output ONLY the improved function implementation""",
                    context=final_solution
                )

        return final_solution