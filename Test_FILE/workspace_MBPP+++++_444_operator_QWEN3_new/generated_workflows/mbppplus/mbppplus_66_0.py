# Workflow ID: mbppplus_66_0
# Benchmark: mbppplus
# Data Indices: [158, 153, 231]

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

        # Phase 1: Multi-perspective problem analysis (Diamond Pattern)
        analysis_tasks = [
            self.generate(
                instruction="""Analyze the INPUT STRUCTURE of this programming problem:
                - What are the expected input types? (string, list, tuple, mixed?)
                - What are the boundary conditions? (empty inputs, single elements, extremes)
                - Are there any implicit type constraints or format expectations?
                - What preconditions must hold for the input to be valid?
                Provide a structured breakdown with clear headings.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the OUTPUT REQUIREMENTS of this programming problem:
                - What is the exact return type? (bool, int, list, tuple, set?)
                - Are there formatting constraints? (order preservation, deduplication, precision)
                - What edge cases must the output handle? (empty results, single values, errors)
                - Are there any post-conditions that must be satisfied?
                Provide a structured breakdown with clear headings.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the ALGORITHMIC STRATEGY for this programming problem:
                - What core operations are needed? (iteration, regex, sorting, set operations, math)
                - What are 2-3 potential solution approaches with their trade-offs?
                - Are there any efficiency constraints? (time/space complexity hints)
                - What Python built-ins or standard library modules would be most appropriate?
                Provide a structured breakdown with clear headings.""",
                context=""
            )
        ]
        
        input_analysis, output_analysis, strategy_analysis = await asyncio.gather(*analysis_tasks)
        
        # Phase 2: Synthesize unified problem schema
        problem_schema = await self.ensemble(
            instruction="""Synthesize these three analyses into a unified problem schema:
            1. Combine input structure, output requirements, and algorithmic strategies
            2. Identify any contradictions or gaps between analyses
            3. Extract all explicit and implicit constraints
            4. List required Python modules (if any)
            5. Define success criteria for the solution
            Format as a structured document with clear sections.""",
            contexts_list=[input_analysis, output_analysis, strategy_analysis]
        )

        # Phase 3: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Generate a Python function that solves the problem according to this schema:
            {problem_schema}
            
            Requirements:
            - Use the exact function name and signature from the problem
            - Include all necessary imports inside the function if needed
            - Handle all edge cases mentioned in the schema
            - Use clear, readable variable names
            - Return the exact expected data type
            - No wrapper code, classes, or extra text - only the function implementation
            - Include defensive programming for unexpected inputs if appropriate""",
            context=problem_schema
        )

        # Phase 4: Validate and potentially revise solution
        validation = await self.generate(
            instruction=f"""Critically review this solution against the problem schema:
            {problem_schema}
            
            Check for:
            - Correct function signature and naming
            - Proper handling of all edge cases
            - Correct return types and formats
            - Logical errors or oversights
            - Efficiency concerns
            - Missing imports or dependencies
            - Compliance with all constraints
            
            If any issues are found, describe them specifically. If perfect, say "VALIDATED".
            """,
            context=initial_solution
        )

        current_solution = initial_solution
        if "VALIDATED" not in validation.upper():
            # Revision loop (up to 3 iterations)
            for i in range(3):
                revised = await self.revise(
                    instruction=f"""Fix the following issues in the solution:
                    {validation}
                    
                    Requirements:
                    - Preserve the core logic where possible
                    - Strengthen edge case handling
                    - Ensure type safety and correct returns
                    - Maintain clean, readable code
                    - Still match exact function signature
                    """,
                    context=current_solution
                )
                
                # Re-validate
                revalidation = await self.generate(
                    instruction=f"""Re-check the revised solution against the problem schema:
                    {problem_schema}
                    
                    Is it now correct? If yes, say "VALIDATED". If still issues, describe them specifically.""",
                    context=revised
                )
                
                current_solution = revised
                if "VALIDATED" in revalidation.upper():
                    break
                validation = revalidation

        # Phase 5: Generate alternative solution for robustness
        alternative_solution = await self.generate(
            instruction=f"""Generate an ALTERNATIVE solution to the same problem using a different approach:
            Problem Schema: {problem_schema}
            
            Requirements:
            - Use a fundamentally different algorithmic strategy than the current solution
            - Still handle all edge cases and constraints
            - Maintain same function signature and return types
            - Could be more/less efficient but must be correct
            - No wrapper code - only the function implementation""",
            context=problem_schema
        )

        # Phase 6: Ensemble best solution
        final_solution = await self.ensemble(
            instruction="""Select the BEST solution between these two options:
            CRITERIA:
            1. Correctness (handles all edge cases, proper types)
            2. Readability and maintainability
            3. Efficiency (time/space complexity)
            4. Robustness (defensive programming, error handling)
            5. Simplicity (fewer moving parts, less complexity)
            
            If one is clearly superior, select it. If they have complementary strengths, 
            create a SYNTHESIZED version that combines the best elements of both.
            
            FINAL OUTPUT MUST BE ONLY THE FUNCTION IMPLEMENTATION with correct signature,
            imports inside function if needed, and no extra text or explanations.""",
            contexts_list=[current_solution, alternative_solution]
        )

        # Phase 7: Format enforcement (final polish)
        polished_solution = await self.revise(
            instruction="""Ensure this code meets EXACT output requirements:
            - ONLY the function implementation (no markdown, no explanations)
            - Correct function name and signature exactly as specified
            - All imports inside the function if needed
            - No wrapper classes or additional functions
            - Proper indentation and Python syntax
            - Return types match exactly what's expected
            - Clean, production-ready code with no debug statements
            
            Strip ALL extra text, comments (unless critical to logic), and formatting.
            Output ONLY the raw Python function code.""",
            context=final_solution
        )

        return polished_solution