# Workflow ID: mbppplus_7_0
# Benchmark: mbppplus
# Data Indices: [130, 161]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import math
        import re
        
        # Phase 1: Comprehensive Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Classify the problem type (mathematical, logical, string, data structure, etc.)
            2. Identify required domain knowledge (formulas, algorithms, edge cases)
            3. Determine input/output types and constraints
            4. List potential edge cases and boundary conditions
            5. Note any implicit requirements or assumptions
            6. Suggest 2-3 possible solution approaches
            7. Identify necessary imports or external libraries
            8. Estimate complexity level (simple, medium, complex)
            
            Format your response as a structured analysis with clear sections.""",
            context=""
        )
        
        # Phase 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                
                Develop a detailed solution strategy focusing on mathematical precision:
                - Break down into computational steps
                - Specify exact formulas or algorithms
                - Handle floating-point precision if needed
                - Include error checking for invalid inputs
                - Suggest appropriate variable names and structure""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                
                Develop a detailed solution strategy focusing on logical clarity:
                - Identify all conditional branches
                - Map out decision trees or lookup tables
                - Ensure comprehensive edge case coverage
                - Suggest clean, readable code structure
                - Consider performance implications""",
                context=problem_analysis
            )
        ]
        
        # Phase 3: Conditional Processing Based on Problem Type
        problem_type_analysis = await self.generate(
            instruction=f"""Analyze this problem classification: {problem_analysis}
            
            Determine the primary problem type and select appropriate processing path:
            - If mathematical (geometry, algebra, calculus): emphasize formula accuracy
            - If logical (conditionals, boolean): emphasize case coverage
            - If string/data: emphasize pattern handling and edge cases
            - If algorithmic: emphasize efficiency and correctness
            
            Also determine if problem requires decomposition into subproblems.
            Return 'mathematical', 'logical', 'string', 'algorithmic', or 'other' as primary classification.""",
            context=problem_analysis
        )
        
        # Execute parallel strategy generation
        strategy_results = await asyncio.gather(*strategy_tasks)
        
        # Synthesize strategies
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best elements from all proposed strategies:
            - Combine mathematical precision with logical clarity
            - Ensure comprehensive edge case handling
            - Optimize for both correctness and readability
            - Include necessary imports and type handling
            - Structure as step-by-step implementation plan
            - Highlight critical validation points""",
            contexts_list=strategy_results
        )
        
        # Phase 4: Conditional Decomposition for Complex Problems
        decomposition_needed = await self.generate(
            instruction=f"""Based on problem analysis: {problem_analysis}
            and synthesized strategy: {synthesized_strategy}
            
            Determine if this problem requires explicit decomposition into subproblems.
            Return 'yes' if problem has multiple distinct computational steps or requires
            solving intermediate values before final result. Return 'no' otherwise.""",
            context=f"{problem_analysis}\n\n{synthesized_strategy}"
        )
        
        if "yes" in decomposition_needed.lower():
            subproblems = await self.decompose(
                instruction=f"""Decompose this problem based on analysis: {problem_analysis}
                and strategy: {synthesized_strategy}
                
                Break into atomic computational steps that can be implemented independently.
                Each subproblem should:
                - Have clear input/output specifications
                - Be solvable with a single function or calculation
                - Include validation criteria
                - Specify dependencies on other subproblems
                
                Focus on creating a clean, testable implementation structure.""",
                context=f"{problem_analysis}\n\n{synthesized_strategy}"
            )
            
            # Generate code for each subproblem in parallel
            subproblem_codes = []
            for subproblem in subproblems:
                subproblem_code = await self.programmer(
                    instruction=f"""Implement this subproblem: {subproblem['description']}
                    
                    Requirements:
                    - Use exact function signature if specified
                    - Include necessary imports
                    - Handle edge cases identified in analysis
                    - Return appropriate data type
                    - Include brief comments explaining key steps
                    - Ensure mathematical precision where needed""",
                    context=f"Problem Analysis: {problem_analysis}\nStrategy: {synthesized_strategy}"
                )
                subproblem_codes.append(subproblem_code)
            
            # Synthesize final solution from subproblem implementations
            final_code = await self.ensemble(
                instruction="""Combine subproblem implementations into complete solution:
                - Ensure proper function signatures as required
                - Integrate subproblems respecting dependencies
                - Add any necessary glue code or coordination logic
                - Include comprehensive error handling
                - Verify all edge cases are addressed
                - Optimize for readability and maintainability""",
                contexts_list=subproblem_codes
            )
        else:
            # Generate complete solution directly for simple problems
            final_code = await self.programmer(
                instruction=f"""Implement complete solution based on:
                Problem Analysis: {problem_analysis}
                Synthesized Strategy: {synthesized_strategy}
                
                Requirements:
                - Use EXACT function signature specified in problem
                - Include ALL necessary imports at top
                - Handle ALL identified edge cases
                - Return correct data type (match expected output type)
                - Ensure mathematical precision for calculations
                - Use clear, descriptive variable names
                - Include brief comments for complex logic
                - Follow Python best practices
                - Code must be production-ready and robust""",
                context=f"{problem_analysis}\n\n{synthesized_strategy}"
            )
        
        # Phase 5: Validation and Refinement Loop
        validation_result = await self.generate(
            instruction=f"""Critically validate this code solution: {final_code}
            
            Check for:
            1. Correct function signature and return type
            2. Proper handling of edge cases identified in analysis
            3. Mathematical accuracy and precision
            4. Logical completeness (all cases covered)
            5. Appropriate imports and dependencies
            6. Readability and maintainability
            7. Potential bugs or logical errors
            8. Compliance with problem requirements
            
            If any issues found, provide specific revision instructions.
            If no issues, return 'VALIDATED'.""",
            context=f"Problem Analysis: {problem_analysis}\nStrategy: {synthesized_strategy}\nCode: {final_code}"
        )
        
        # Conditional refinement
        if "VALIDATED" not in validation_result:
            final_code = await self.revise(
                instruction=f"""Revise code based on validation feedback: {validation_result}
                
                Specific requirements:
                - Fix all identified issues
                - Maintain original function signature
                - Preserve core logic while correcting errors
                - Add missing edge case handling
                - Improve clarity where needed
                - Ensure mathematical precision
                - Verify type consistency
                - Keep code concise and readable""",
                context=final_code
            )
        
        # Final extraction of clean code
        clean_code = await self.generate(
            instruction=f"""Extract ONLY the final Python code from this response: {final_code}
            
            Requirements:
            - Include ONLY the function implementation with necessary imports
            - Use EXACT function name from problem
            - Preserve function signature including parameter names
            - Do NOT wrap in any outer function or class
            - Return appropriate data types as shown in tests
            - Remove any explanatory text, markdown, or additional commentary
            - Code must be ready for direct execution""",
            context=final_code
        )
        
        return clean_code