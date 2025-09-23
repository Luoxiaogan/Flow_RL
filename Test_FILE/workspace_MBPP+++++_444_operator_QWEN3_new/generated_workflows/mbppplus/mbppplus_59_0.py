# Workflow ID: mbppplus_59_0
# Benchmark: mbppplus
# Data Indices: [227, 59, 335]

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

        # Step 1: Classify problem and extract core requirements
        classification = await self.generate(
            instruction="""Analyze the programming problem deeply:
            1. Identify the primary category: string manipulation, list/tuple operations, mathematical computation, interval logic, or other.
            2. Extract expected input types and output types from the function signature.
            3. Infer key operations needed: iteration, mapping, filtering, min/max, counting, etc.
            4. Note any explicit or implicit constraints mentioned.
            5. Predict likely edge cases: empty inputs, single elements, duplicates, boundary values.
            Present as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Validate and refine classification
        validated_classification = await self.revise(
            instruction="""Critique this problem classification:
            - Does it miss any key aspects of the problem?
            - Are the inferred operations appropriate?
            - Are edge cases comprehensive?
            - Is the output format correctly anticipated?
            Improve the analysis with any missing insights or corrections.""",
            context=classification
        )

        # Step 3: Generate multiple solution candidates in parallel
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a SIMPLE, straightforward solution based on:
                Classification: {validated_classification}
                
                Focus on clarity and direct implementation. Assume basic edge cases but prioritize core logic.
                Return ONLY the function implementation with necessary imports inside the function if needed.
                Match the exact function signature and return type specified.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a ROBUST, edge-case hardened solution based on:
                Classification: {validated_classification}
                
                Explicitly handle all predicted edge cases. Add defensive checks if needed.
                Prioritize correctness over brevity. Return ONLY the function implementation with necessary imports inside the function if needed.
                Match the exact function signature and return type specified.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an EFFICIENT, optimized solution based on:
                Classification: {validated_classification}
                
                Focus on minimal operations and optimal data structures. Consider time/space complexity.
                Still handle critical edge cases. Return ONLY the function implementation with necessary imports inside the function if needed.
                Match the exact function signature and return type specified.""",
                context=""
            )
        ]
        
        candidates = await asyncio.gather(*candidate_tasks)

        # Step 4: Critique each candidate against edge cases and requirements
        revised_candidates = []
        for i, candidate in enumerate(candidates):
            critique = await self.revise(
                instruction=f"""Critically evaluate this solution candidate:
                - Does it handle all edge cases identified in: {validated_classification}?
                - Does it match the required function signature and return type exactly?
                - Are there any logical flaws or potential failures?
                - Is the code clean and readable?
                
                Revise the solution to fix any issues found. If no issues, return the original.
                Return ONLY the function implementation with necessary imports inside the function if needed.""",
                context=candidate
            )
            revised_candidates.append(critique)

        # Step 5: Ensemble - Synthesize best solution
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution from the candidates:
            - Prioritize correctness and edge-case handling above all.
            - Ensure exact match of function signature and return type.
            - Prefer clean, readable code.
            - If one solution is clearly superior, select it. If elements from multiple are needed, merge them.
            Return ONLY the final function implementation with necessary imports inside the function if needed.""",
            contexts_list=revised_candidates
        )

        # Step 6: Final validation and formatting check
        validated_solution = await self.revise(
            instruction="""Final quality check:
            - Verify function name, parameters, and return type match specification exactly.
            - Ensure no extra text, explanations, or markdown - only pure Python code.
            - Confirm all necessary imports are inside the function if required.
            - Check that edge cases from classification are handled.
            Return the cleaned, final implementation.""",
            context=final_solution
        )

        return validated_solution