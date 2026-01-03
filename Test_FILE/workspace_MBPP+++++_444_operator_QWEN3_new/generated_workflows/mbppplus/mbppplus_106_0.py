# Workflow ID: mbppplus_106_0
# Benchmark: mbppplus
# Data Indices: [258, 330, 121]

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
        import json
        import re

        # Phase 1: Comprehensive Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Extract and structure the following information:
            1. INPUT SPECIFICATION: What are the input parameters? What data types? What constraints?
            2. OUTPUT SPECIFICATION: What should be returned? Exact data type and structure?
            3. TRANSFORMATION RULE: What is the core logic or mathematical relationship?
            4. EDGE CASES: What are the boundary conditions? (empty inputs, single elements, zeros, negatives, etc.)
            5. ALGORITHM CATEGORY: Is this combinatorial, mathematical, filtering, string manipulation, or other?
            6. KEY OPERATIONS: What specific operations are needed? (iteration, recursion, set operations, arithmetic, etc.)
            
            Format your response as a structured analysis with clear section headers. Be exhaustive and precise.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Analyze this problem from a MATHEMATICAL perspective:
                - Identify any mathematical formulas, series, or patterns
                - Derive the underlying mathematical relationship
                - Consider closed-form solutions vs iterative approaches
                - What mathematical properties or theorems apply?
                
                Problem Analysis Context:
                {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Analyze this problem from a DATA STRUCTURE perspective:
                - What data structures are involved? (lists, dicts, sets, tuples)
                - What operations are needed? (filtering, mapping, combining, transforming)
                - Are there ordering or uniqueness requirements?
                - How should edge cases be handled structurally?
                
                Problem Analysis Context:
                {problem_analysis}""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Analyze this problem from an ALGORITHMIC perspective:
                - What algorithmic paradigms apply? (brute force, greedy, divide-and-conquer, etc.)
                - What is the optimal time/space complexity?
                - Are there standard algorithms or patterns that solve this?
                - How can the solution be made robust and efficient?
                
                Problem Analysis Context:
                {problem_analysis}""",
                context=problem_analysis
            )
        ]
        
        strategy_analyses = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a unified implementation strategy:
            1. Combine the strongest insights from each analysis
            2. Resolve any contradictions or conflicts
            3. Create a step-by-step implementation plan
            4. Explicitly address all identified edge cases
            5. Specify the exact algorithm and data structures to use
            6. Outline the code structure and key operations
            
            The output should be a comprehensive, actionable blueprint for implementation.""",
            contexts_list=strategy_analyses
        )

        # Phase 4: Pseudocode Blueprint Generation
        pseudocode_blueprint = await self.generate(
            instruction=f"""Create a detailed pseudocode blueprint based on this strategy:
            - Use clear, structured, language-agnostic pseudocode
            - Include all edge case handling explicitly
            - Specify input validation and error handling
            - Outline the exact steps of the algorithm
            - Include comments for complex logic sections
            
            Strategy Context:
            {synthesized_strategy}""",
            context=synthesized_strategy
        )

        # Phase 5: Code Implementation
        initial_implementation = await self.generate(
            instruction=f"""Generate the final Python implementation based on this pseudocode blueprint:
            - Use the EXACT function name and signature specified in the problem
            - Include all necessary imports at the top of the function
            - Handle all edge cases identified in the analysis
            - Return the EXACT data type specified (list, tuple, dict, etc.)
            - Write clean, readable, efficient code
            - Include minimal but clear comments for complex sections
            - DO NOT include any test cases or print statements
            
            Pseudocode Blueprint:
            {pseudocode_blueprint}""",
            context=pseudocode_blueprint
        )

        # Phase 6: Validation and Refinement Loop
        code_to_refine = initial_implementation
        max_iterations = 3
        
        for iteration in range(max_iterations):
            validation_result = await self.generate(
                instruction=f"""Rigorously validate this implementation:
                1. Check if function signature matches exactly
                2. Verify all edge cases are handled (empty inputs, single elements, boundaries)
                3. Confirm return type matches specification
                4. Test logical correctness with sample inputs
                5. Identify any bugs, inefficiencies, or style issues
                
                If any issues are found, describe them specifically. If perfect, say "VALIDATION PASSED".
                
                Implementation to Validate:
                {code_to_refine}""",
                context=code_to_refine
            )
            
            # Conditional branching based on validation
            if "VALIDATION PASSED" in validation_result or "passed" in validation_result.lower():
                break
            else:
                code_to_refine = await self.revise(
                    instruction=f"""Revise the implementation to fix all issues identified in validation:
                    Validation Issues:
                    {validation_result}
                    
                    Original Implementation:
                    {code_to_refine}
                    
                    Requirements:
                    - Fix all identified bugs and issues
                    - Maintain exact function signature
                    - Preserve all edge case handling
                    - Keep code clean and efficient
                    - Return the implementation only (no explanations)""",
                    context=code_to_refine
                )

        # Phase 7: Final Sanitization and Output
        final_implementation = await self.revise(
            instruction="""Sanitize this code for final output:
            - Remove any explanatory text, comments about the process, or meta-information
            - Keep only the pure Python function implementation with necessary imports
            - Ensure imports are at the top inside the function if needed
            - Verify the function name and signature are exactly as specified
            - Remove any test cases, print statements, or example usage
            - Return ONLY the clean implementation ready for execution""",
            context=code_to_refine
        )

        return final_implementation