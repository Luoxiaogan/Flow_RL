# Workflow ID: humaneval_61_0
# Benchmark: humaneval
# Data Indices: [97, 128]

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
        """
        Universal workflow for generating Python functions from specifications.
        This workflow analyzes the problem, generates multiple solution candidates,
        synthesizes the best approach, and refines it to match requirements.
        """
        import asyncio
        import re

        # Step 1: Comprehensive problem analysis
        analysis = await self.generate(
            instruction="""Perform deep analysis of this code generation problem:
            1. Extract the exact function signature and name (MUST match ENTRY POINT)
            2. Identify the core transformation or calculation being requested
            3. Analyze all provided examples to understand input-output relationships
            4. Note any edge cases mentioned or implied in examples
            5. Determine expected return type (int, float, None, etc.)
            6. Identify any constraints or assumptions stated
            7. Classify problem type (mathematical, array processing, string manipulation, etc.)
            8. Note any special handling required (negative numbers, empty inputs, etc.)
            
            Format your analysis as a structured breakdown with clear sections.
            Be meticulous - the examples are your test cases and must be satisfied exactly.""",
            context=""
        )

        # Step 2: Generate multiple solution approaches in parallel
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function solution based on this analysis:
                {analysis}
                
                Approach 1: Focus on mathematical/algorithmic elegance
                - Use minimal, efficient operations
                - Prioritize clarity and directness
                - Handle edge cases explicitly
                - Return exactly what's specified (no extra functionality)
                - Function name MUST match ENTRY POINT exactly""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a Python function solution based on this analysis:
                {analysis}
                
                Approach 2: Focus on robustness and edge case handling
                - Explicitly handle all edge cases mentioned in examples
                - Use defensive programming where appropriate
                - Include clear logic for special cases
                - Return exactly what's specified (no extra functionality)
                - Function name MUST match ENTRY POINT exactly""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a Python function solution based on this analysis:
                {analysis}
                
                Approach 3: Focus on literal interpretation of examples
                - Implement solution that directly maps example inputs to outputs
                - Follow patterns observed in examples precisely
                - Don't generalize beyond what examples demonstrate
                - Return exactly what's specified (no extra functionality)
                - Function name MUST match ENTRY POINT exactly""",
                context=analysis
            )
        )

        # Step 3: Ensemble - select and synthesize the best solution
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these candidates:
            {analysis}
            
            Evaluate each candidate against these criteria:
            1. Correctness: Does it satisfy all provided examples?
            2. Precision: Does it return exactly the specified type?
            3. Completeness: Does it handle all edge cases from examples?
            4. Minimalism: Does it implement only what's specified?
            5. Naming: Does function name exactly match ENTRY POINT?
            
            If one candidate is clearly superior, select it.
            If multiple are good, synthesize a combined solution.
            If all have flaws, create a new solution addressing the flaws.
            
            Output ONLY the final Python function code, nothing else.
            The code must be ready to run and pass all test cases.""",
            contexts_list=solution_candidates
        )

        # Step 4: Final refinement for precision and compliance
        final_code = await self.revise(
            instruction="""Refine this code to ensure absolute compliance:
            1. Verify function name EXACTLY matches ENTRY POINT (case-sensitive)
            2. Ensure return types match examples precisely (int vs float matters)
            3. Remove any unnecessary imports, comments, or extra functionality
            4. Simplify to minimal implementation that satisfies all examples
            5. Handle edge cases exactly as demonstrated in examples
            6. No over-engineering - implement exactly what's specified
            
            Output ONLY the clean Python function code, nothing else.
            The code must be production-ready and pass all hidden test cases.""",
            context=synthesized_solution
        )

        return final_code