# Workflow ID: mbppplus_75_0
# Benchmark: mbppplus
# Data Indices: [140, 255, 237]

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

        # Step 1: Parallel problem analysis from multiple perspectives
        analysis_tasks = [
            self.generate(
                instruction="""Analyze this programming problem from a MATHEMATICAL perspective:
                - Identify any underlying mathematical properties, invariants, or necessary conditions
                - Derive equations or relationships that must hold for a solution to exist
                - Consider parity, symmetry, or combinatorial constraints
                - What edge cases might break naive solutions?
                - Format your analysis as structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an ALGORITHMIC perspective:
                - What core algorithmic patterns apply? (iteration, recursion, greedy, DP, etc.)
                - What data structures are most suitable?
                - What is the expected time/space complexity?
                - How would you handle edge cases (empty input, single element, uniform input)?
                - Format your analysis as structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a ROBUSTNESS perspective:
                - List all possible edge cases (including type, size, and value boundaries)
                - What input assumptions are safe to make? Which are dangerous?
                - How should errors or invalid inputs be handled?
                - What return types and formats are strictly required?
                - Format your analysis as structured bullet points.""",
                context=""
            )
        ]
        
        analyses = await asyncio.gather(*analysis_tasks)
        
        # Step 2: Synthesize analyses into unified strategy
        strategy = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent solution strategy:
            - Resolve any contradictions between perspectives
            - Prioritize mathematical soundness and edge-case coverage
            - Extract key steps for implementation
            - Identify critical constraints and invariants
            - Format as numbered steps with clear rationale for each""",
            contexts_list=analyses
        )

        # Step 3: Generate initial implementation
        draft = await self.generate(
            instruction=f"""Implement the solution according to this strategy:
            {strategy}
            
            STRICT REQUIREMENTS:
            - Use the exact function signature provided
            - Handle all edge cases identified in the robustness analysis
            - Return the correct data type (bool, int, etc.) as specified
            - Include necessary imports inside the function if needed
            - Write clean, readable code with meaningful variable names
            - Do NOT include test cases or print statements""",
            context=""
        )

        # Step 4: Iterative refinement with edge-case simulation
        current_code = draft
        for i in range(3):  # Max 3 refinement iterations
            critique = await self.generate(
                instruction=f"""Critique this implementation by simulating edge cases:
                - Generate 5 challenging test cases (including edge cases)
                - For each, predict the output and verify against expected behavior
                - Identify any logic flaws, type mismatches, or unhandled cases
                - Rate confidence in correctness (1-10)
                - If confidence >= 9, state "SATISFACTORY"
                
                Current code:
                {current_code}""",
                context=current_code
            )
            
            if "SATISFACTORY" in critique.upper() or i == 2:  # Last iteration
                break
                
            current_code = await self.revise(
                instruction=f"""Revise the implementation to fix all identified issues:
                Critique: {critique}
                
                Requirements:
                - Preserve correct logic while fixing flaws
                - Prioritize edge-case handling
                - Maintain clean, readable code
                - Ensure type consistency with function signature""",
                context=current_code
            )

        # Step 5: Generate alternative implementation for cross-verification
        alternative = await self.generate(
            instruction=f"""Generate an ALTERNATIVE implementation using a different approach:
            - If original is iterative, use functional or mathematical approach
            - If original uses counters, use sets or direct comparison
            - Maintain same function signature and edge-case handling
            - Focus on simplicity and readability
            
            Strategy context:
            {strategy}""",
            context=""
        )

        # Step 6: Final ensemble selection
        final_code = await self.ensemble(
            instruction="""Select the BEST implementation based on:
            - Correctness (handles all edge cases)
            - Simplicity and readability
            - Efficiency (time/space complexity)
            - Robustness (type safety, error handling)
            
            If one solution is clearly superior, select it.
            If both have strengths, MERGE them into an optimal hybrid.
            
            Return ONLY the final implementation code with no additional text.""",
            contexts_list=[current_code, alternative]
        )

        return final_code