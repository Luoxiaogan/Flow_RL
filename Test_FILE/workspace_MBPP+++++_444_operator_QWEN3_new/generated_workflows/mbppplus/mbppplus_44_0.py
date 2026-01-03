# Workflow ID: mbppplus_44_0
# Benchmark: mbppplus
# Data Indices: [43, 48, 14]

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
        
        # Phase 1: Deep problem analysis and classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Extract and structure the following:
            1. INPUT SPECIFICATION: What are the input parameters? What data types are expected? Any constraints?
            2. OUTPUT SPECIFICATION: What should be returned? Exact data type and structure required.
            3. TRANSFORMATION LOGIC: What operation needs to be performed? Describe the algorithm in plain English.
            4. EDGE CASES: What boundary conditions must be handled? (empty inputs, single elements, out-of-bounds, etc.)
            5. CATEGORY CLASSIFICATION: Classify this problem into one or more categories: 
               - Array/List Slicing & Manipulation
               - Mathematical Aggregation
               - Data Structure Transformation
               - Conditional Processing
               - Other (specify)
            6. TEST CASE ANALYSIS: Based on any provided examples, infer additional hidden requirements.
            Present your analysis in clear, structured sections with headings.""",
            context=""
        )

        # Phase 2: Generate three distinct solution strategies in parallel
        strategy_instructions = [
            """Implement the most straightforward, literal solution possible. 
            - Use basic Python constructs that directly mirror the problem description.
            - Prioritize readability and explicit logic over cleverness.
            - Include comments explaining each step.
            - Do not optimize prematurely.""",
            
            """Implement the most concise and efficient solution possible.
            - Use advanced Python features (slicing, comprehensions, built-ins) where appropriate.
            - Minimize lines of code while maintaining correctness.
            - Assume inputs are well-formed unless edge cases are explicitly mentioned.
            - Focus on algorithmic elegance.""",
            
            """Implement a defensively robust solution.
            - Explicitly handle all edge cases identified in the analysis.
            - Include input validation where appropriate.
            - Use clear variable names and structure to make failure modes obvious.
            - Prioritize correctness and robustness over performance or brevity."""
        ]

        # Generate solutions in parallel
        initial_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on this problem analysis:
                {problem_analysis}
                
                {strategy_instructions[i]}
                
                IMPORTANT: Output ONLY the Python function implementation. 
                Include necessary imports. Match the exact function signature. 
                No explanations, no markdown, no extra text.""",
                context=problem_analysis
            ) for i in range(3)]
        )

        # Phase 3: Revise each solution for correctness and robustness
        revised_solutions = []
        for i, solution in enumerate(initial_solutions):
            revised = await self.revise(
                instruction=f"""Critically review and improve this solution:
                - Verify it handles all edge cases mentioned in the problem analysis.
                - Ensure type consistency (returning list vs tuple vs set as required).
                - Check for off-by-one errors, index bounds, and empty input handling.
                - Improve clarity if needed, but preserve the core approach.
                - Fix any logical errors or inefficiencies.
                
                Problem Analysis for reference:
                {problem_analysis}
                
                IMPORTANT: Output ONLY the improved Python function implementation. 
                No explanations, no markdown, no extra text.""",
                context=solution
            )
            revised_solutions.append(revised)

        # Phase 4: Ensemble - Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""You are an expert code reviewer selecting the best implementation. Criteria:
            1. CORRECTNESS: Must handle all test cases and edge cases correctly.
            2. ROBUSTNESS: Gracefully handles invalid inputs or edge conditions.
            3. READABILITY: Code is clear and maintainable.
            4. EFFICIENCY: Reasonably efficient without premature optimization.
            
            If one solution clearly dominates, select it. Otherwise, synthesize a hybrid that combines the best elements.
            CRITICAL: Output ONLY the final Python function implementation. 
            Include necessary imports. Match the exact function signature. 
            NO explanations, NO markdown, NO extra text - just the code.""",
            contexts_list=revised_solutions
        )

        # Phase 5: Final sanitization - ensure pure code output
        sanitized_solution = await self.generate(
            instruction="""Extract ONLY the Python function implementation from the following text. 
            Remove ALL explanations, markdown, comments (unless they're part of the original code logic), 
            and any extra text. The output must be pure, runnable Python code that matches the required 
            function signature exactly. If the input is already pure code, return it unchanged.""",
            context=final_solution
        )

        return sanitized_solution