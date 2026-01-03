# Workflow ID: mbppplus_118_0
# Benchmark: mbppplus
# Data Indices: [319, 352, 323]

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

        # Phase 1: Problem Classification and Complexity Assessment
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:
            1. Classify the problem type: Is it about lists/tuples, strings, math, logic, or data structures?
            2. Identify the core operation: filtering, transformation, aggregation, comparison, etc.
            3. Assess complexity: Are there obvious edge cases (empty inputs, duplicates, type boundaries)?
            4. Determine if the problem is trivial (e.g., max_of_two) or requires nuanced handling.
            5. Based on this, recommend a solution strategy: 'direct', 'parallel', or 'deep_validation'.
            Return your analysis in a structured format with clear labels.""",
            context=""
        )

        # Phase 2: Strategy Selection and Branching
        if "trivial" in classification.lower() or "direct" in classification.lower():
            # Simple problems: single generate + revise
            solution = await self.generate(
                instruction="""Implement the function exactly as specified:
                - Study the function signature and test cases carefully.
                - Handle edge cases: empty inputs, single elements, duplicates, type boundaries.
                - Return ONLY the function implementation as a string, with necessary imports.
                - Match the exact function name and parameter names.
                - Ensure return type matches test expectations (list vs tuple vs string, etc.).
                Do not include explanations or markdown.""",
                context=""
            )
            
            refined = await self.revise(
                instruction="""Critically review this solution:
                1. Does it handle all edge cases mentioned in the problem?
                2. Does it match the expected output type and format?
                3. Are there any assumptions that might break on edge inputs?
                4. Is the code clean, efficient, and readable?
                Return the corrected implementation if any issues are found, otherwise return as-is.
                ONLY return the function code, nothing else.""",
                context=solution
            )
            return refined

        else:
            # Complex problems: parallel generation with diverse strategies
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction="""Generate solution focusing on literal test case compliance:
                    - Implement exactly what the test cases demonstrate.
                    - Prioritize matching output format and type.
                    - Include explicit handling for edge cases shown or implied.
                    - Return ONLY the function code with necessary imports.""",
                    context=""
                ),
                self.generate(
                    instruction="""Generate solution by generalizing from problem structure:
                    - Ignore specific test values; focus on the underlying pattern.
                    - Design for robustness: handle empty, single, duplicate, boundary cases.
                    - Use efficient and readable constructs.
                    - Return ONLY the function code with necessary imports.""",
                    context=""
                ),
                self.generate(
                    instruction="""Generate solution with defensive programming focus:
                    - Assume inputs can be malformed or extreme.
                    - Add implicit checks for edge conditions even if not shown in tests.
                    - Prioritize correctness over brevity.
                    - Return ONLY the function code with necessary imports.""",
                    context=""
                )
            )

            # Phase 3: Parallel Validation
            validation_tasks = []
            for attempt in solution_attempts:
                validated = self.revise(
                    instruction="""Simulate test cases mentally:
                    1. Walk through each provided test case with this implementation.
                    2. Check for type mismatches, off-by-one errors, or logic flaws.
                    3. Consider untested edge cases: empty inputs, None values, duplicates, type boundaries.
                    4. If any failure is detected, revise the code to fix it.
                    5. If confident, return the code unchanged.
                    ONLY return the final function implementation, nothing else.""",
                    context=attempt
                )
                validation_tasks.append(validated)
            
            validated_solutions = await asyncio.gather(*validation_tasks)

            # Phase 4: Ensemble Selection
            final_solution = await self.ensemble(
                instruction="""Select the best solution from the candidates below:
                Criteria in order of priority:
                1. Correctness: Must pass all test cases and handle implied edge cases.
                2. Robustness: Graceful handling of unexpected inputs or edge conditions.
                3. Efficiency: Avoid unnecessary complexity or operations.
                4. Clarity: Clean, readable, well-structured code.
                
                Analyze each candidate against these criteria. If one is clearly superior, select it.
                If multiple are equally good, synthesize a hybrid that combines their strengths.
                Return ONLY the final function implementation as a string, with necessary imports.
                Do not include any explanations or markdown.""",
                contexts_list=validated_solutions
            )

            return final_solution