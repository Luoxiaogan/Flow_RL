# Workflow ID: mbppplus_40_0
# Benchmark: mbppplus
# Data Indices: [325, 25]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
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
        """
        Universal problem-solving workflow for programming challenges.
        Dynamically adapts strategy based on problem characteristics.
        """
        import asyncio
        import re

        # Phase 1: Problem Analysis and Classification
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it:
            1. Identify the problem category (mathematical, combinatorial, geometric, string manipulation, etc.)
            2. Determine the expected input/output types and formats
            3. Extract any explicit or implicit constraints
            4. Identify key mathematical or algorithmic concepts involved
            5. Note any edge cases or special conditions mentioned
            6. Assess complexity level (simple, moderate, complex)
            7. Suggest 2-3 potential solution approaches
            8. Predict potential pitfalls or common mistakes
            
            Structure your response with clear section headers for each point above.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        # Generate multiple solution approaches simultaneously
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                Develop a RECURSIVE solution approach:
                - Define base cases clearly
                - Specify recursive relationship
                - Consider memoization if applicable
                - Handle edge cases explicitly
                - Provide pseudocode outline""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                Develop an ITERATIVE/DYNAMIC PROGRAMMING solution approach:
                - Define state variables
                - Specify transition logic
                - Consider space/time complexity
                - Handle edge cases explicitly
                - Provide pseudocode outline""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                Develop a DIRECT FORMULA/MATHEMATICAL solution approach:
                - Identify applicable mathematical formulas
                - Derive closed-form solution if possible
                - Consider numerical stability
                - Handle edge cases explicitly
                - Provide step-by-step calculation method""",
                context=problem_analysis
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Synthesis and Selection
        synthesized_strategy = await self.ensemble(
            instruction="""Evaluate and synthesize the three solution approaches:
            1. Compare approaches based on: correctness, efficiency, simplicity, and robustness
            2. Select the most appropriate approach for this specific problem
            3. If multiple approaches are equally valid, create a hybrid solution
            4. Justify your selection with specific references to problem requirements
            5. Outline the final implementation plan with clear steps
            6. Include specific handling for identified edge cases
            
            Format as: SELECTED APPROACH: [name] followed by detailed implementation plan""",
            contexts_list=strategy_results
        )

        # Phase 4: Code Generation with Validation
        initial_code = await self.programmer(
            instruction=f"""Implement the selected solution approach:
            {synthesized_strategy}
            
            Requirements:
            - Use EXACT function name and signature from problem
            - Include all necessary imports
            - Handle all identified edge cases
            - Return correct data type
            - Include minimal but clear comments
            - Optimize for correctness over performance (unless specified otherwise)
            
            IMPORTANT: Generate ONLY the function implementation as specified in output requirements.""",
            context=synthesized_strategy
        )

        # Phase 5: Solution Validation and Refinement Loop
        max_refinement_iterations = 3
        current_code = initial_code
        refinement_history = []

        for iteration in range(max_refinement_iterations):
            # Validate current solution
            validation_analysis = await self.generate(
                instruction=f"""Critically analyze this code solution:
                {current_code}
                
                Check for:
                1. Correctness against problem requirements
                2. Edge case handling (empty inputs, boundary values, etc.)
                3. Data type consistency
                4. Potential bugs or logical errors
                5. Efficiency concerns
                6. Code clarity and maintainability
                
                If issues found, provide specific, actionable fixes.
                If no issues, state "VALIDATED: Solution appears correct."""",
                context=current_code
            )

            # Check if validation passed
            if "VALIDATED" in validation_analysis and "correct" in validation_analysis.lower():
                break

            # Refine code based on validation feedback
            refined_code = await self.revise(
                instruction=f"""Revise the code based on this validation feedback:
                {validation_analysis}
                
                Requirements:
                - Fix all identified issues
                - Maintain original function signature
                - Preserve working parts of solution
                - Improve clarity where needed
                - Add comments for complex logic
                
                Generate ONLY the revised function implementation.""",
                context=current_code
            )
            
            refinement_history.append({
                'iteration': iteration + 1,
                'feedback': validation_analysis,
                'revised_code': refined_code
            })
            current_code = refined_code

        # Phase 6: Final Output Preparation
        final_output = await self.revise(
            instruction="""Prepare the final solution for submission:
            1. Ensure code follows EXACT output requirements
            2. Remove any unnecessary comments or debug code
            3. Verify function signature matches exactly
            4. Ensure all imports are included at top
            5. Format code cleanly with proper indentation
            6. Double-check edge case handling
            
            Generate ONLY the final function implementation as specified in output requirements.""",
            context=current_code
        )

        return final_output