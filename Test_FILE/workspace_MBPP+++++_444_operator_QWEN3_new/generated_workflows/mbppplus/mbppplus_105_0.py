# Workflow ID: mbppplus_105_0
# Benchmark: mbppplus
# Data Indices: [230, 241, 179]

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
        
        # Phase 1: Comprehensive problem analysis and classification
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Identify the core task: What transformation is being performed? (counting, searching, combining, filtering, etc.)
            2. Determine data types: What input/output types are involved? (lists, tuples, sets, numbers, strings)
            3. Extract constraints: What special conditions must be satisfied? (order preservation, uniqueness, edge cases)
            4. Recognize patterns: Does this resemble known algorithmic patterns? (two-pointer, sliding window, combinatorial, etc.)
            5. Identify key operations: What fundamental operations are needed? (comparisons, arithmetic, set operations, etc.)
            6. Note edge cases: What boundary conditions should be considered? (empty inputs, single elements, duplicates, etc.)
            
            Format your analysis as a structured JSON-like response with clear sections for each category above.
            Be thorough and precise - this analysis will guide all subsequent solution development.""",
            context=""
        )

        # Phase 2: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this problem analysis:
                {problem_analysis}
                
                Develop a MATHEMATICAL/FORMULA-BASED solution strategy:
                - Express the problem in mathematical terms
                - Derive formulas or equations that solve it
                - Consider algebraic simplifications
                - Focus on computational efficiency
                - Handle edge cases mathematically
                Provide detailed step-by-step reasoning.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this problem analysis:
                {problem_analysis}
                
                Develop an ALGORITHMIC/ITERATIVE solution strategy:
                - Design step-by-step procedural approach
                - Consider loop structures and iteration patterns
                - Handle edge cases through conditional logic
                - Focus on clarity and readability
                - Consider time/space complexity
                Provide detailed pseudocode with explanations.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this problem analysis:
                {problem_analysis}
                
                Develop a FUNCTIONAL/DATA-TRANSFORMATION solution strategy:
                - Think in terms of data transformations
                - Consider using built-in functions or libraries
                - Focus on declarative rather than imperative style
                - Handle edge cases through functional composition
                - Consider using map/filter/reduce patterns
                Provide detailed transformation steps with explanations.""",
                context=problem_analysis
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)
        
        # Phase 3: Synthesize best approach from multiple strategies
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the most effective solution approach from the three strategies provided.
            Consider:
            - Which approach is most aligned with the problem requirements?
            - Which handles edge cases most comprehensively?
            - Which is most efficient and readable?
            - Can elements from different strategies be combined for a superior solution?
            - What potential pitfalls should be avoided?
            
            Produce a unified, step-by-step solution plan that incorporates the best elements from all strategies.
            Be specific about implementation details and include explicit handling of edge cases.
            Format as clear, numbered steps with justifications for key decisions.""",
            contexts_list=strategy_results
        )

        # Phase 4: Generate initial code implementation
        initial_implementation = await self.generate(
            instruction=f"""Implement the solution according to this synthesized strategy:
            {synthesized_strategy}
            
            Requirements:
            - Use EXACT function name and signature from the problem
            - Include all necessary imports at the top
            - Handle all edge cases identified in analysis
            - Match expected return types precisely
            - Write clean, readable, well-commented code
            - Follow Python best practices
            - Ensure type consistency throughout
            
            IMPORTANT: Return ONLY the function implementation as specified in the output requirements.
            No additional text, explanations, or markdown formatting.""",
            context=synthesized_strategy
        )

        # Phase 5: Rigorous validation and refinement loop
        current_implementation = initial_implementation
        max_iterations = 3
        
        for i in range(max_iterations):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this implementation:
                {current_implementation}
                
                Check for:
                1. Correctness: Does it solve the core problem correctly?
                2. Edge cases: Does it handle empty inputs, single elements, duplicates, etc.?
                3. Type safety: Are input/output types handled correctly?
                4. Efficiency: Is the solution reasonably efficient?
                5. Readability: Is the code clear and well-structured?
                6. Requirements: Does it match all specified requirements?
                
                If issues are found, provide specific, actionable feedback for improvement.
                If no issues are found, state "VALIDATED: No issues found".
                
                Be thorough and precise in your validation.""",
                context=current_implementation
            )
            
            if "VALIDATED: No issues found" in validation_feedback:
                break
                
            # Revise implementation based on feedback
            current_implementation = await self.revise(
                instruction=f"""Revise the implementation based on this feedback:
                {validation_feedback}
                
                Requirements:
                - Address all issues raised in the feedback
                - Maintain correct function signature
                - Preserve working functionality while fixing problems
                - Improve code quality and robustness
                - Handle additional edge cases if identified
                - Return ONLY the function implementation (no explanations)
                
                Make minimal necessary changes to fix identified issues.""",
                context=current_implementation
            )
        
        # Phase 6: Final quality assurance and formatting
        final_implementation = await self.revise(
            instruction="""Perform final quality assurance:
            1. Verify function signature matches exactly what was specified
            2. Ensure all imports are included and properly placed
            3. Confirm code is properly formatted with consistent indentation
            4. Remove any debug statements or unnecessary comments
            5. Ensure return statement is correct and in right position
            6. Verify no extra text or markdown formatting is included
            
            Return ONLY the clean, final function implementation as specified.
            This is the final output that will be executed, so it must be perfect.""",
            context=current_implementation
        )
        
        return final_implementation