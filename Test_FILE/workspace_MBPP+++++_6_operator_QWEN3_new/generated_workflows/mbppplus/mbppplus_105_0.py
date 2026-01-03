# Workflow ID: mbppplus_105_0
# Benchmark: mbppplus
# Data Indices: [44, 18]

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
        import re
        
        # Phase 1: Problem Classification and Requirement Extraction
        classification = await self.generate(
            instruction="""Perform deep analysis of this programming problem. Extract:
            1. Problem category (string manipulation, data structure, mathematical, etc.)
            2. Input type and structure (list of tuples, string, etc.)
            3. Output type and structure (integer, string, etc.)
            4. Key transformation rules or operations needed
            5. Edge cases that must be handled (empty inputs, single elements, etc.)
            6. Any constraints or special conditions
            7. Expected function signature if available
            8. Reference solution approach if visible (without copying)
            
            Format your response as a structured analysis with clear sections.""",
            context=""
        )
        
        # Summarize classification into actionable requirements
        requirements = await self.summarize(
            instruction="""Condense the problem analysis into a concise, structured requirements specification.
            Include:
            - Problem type classification
            - Exact input/output specifications
            - Critical edge cases to handle
            - Key operations needed
            - Function signature requirements
            - Style/formatting expectations
            
            Format as bullet points for easy consumption by subsequent steps.""",
            context=classification
        )
        
        # Phase 2: Parallel Strategy Generation
        # Generate multiple solution approaches in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on requirements: {requirements}
                
                Generate a solution strategy using imperative programming approach:
                - Focus on clear, step-by-step procedural logic
                - Use loops and conditionals as primary constructs
                - Handle edge cases explicitly
                - Prioritize readability and direct implementation
                - Include specific variable names and structure suggestions""",
                context=requirements
            ),
            self.generate(
                instruction=f"""Based on requirements: {requirements}
                
                Generate a solution strategy using functional programming approach:
                - Focus on map/filter/reduce patterns
                - Use list comprehensions and higher-order functions
                - Emphasize immutability and expression-based logic
                - Consider itertools or functools if applicable
                - Include specific function composition suggestions""",
                context=requirements
            ),
            self.generate(
                instruction=f"""Based on requirements: {requirements}
                
                Generate a solution strategy using mathematical/set-based approach:
                - Look for mathematical patterns or formulas
                - Consider set operations, combinatorics, or algebraic transformations
                - Use built-in functions and libraries where appropriate
                - Focus on efficiency and elegance
                - Include specific mathematical insights or optimizations""",
                context=requirements
            )
        ]
        
        strategies = await asyncio.gather(*strategy_tasks)
        
        # Ensemble: Synthesize best approach
        selected_strategy = await self.ensemble(
            instruction="""Evaluate the three solution strategies and synthesize the optimal approach:
            1. Assess each strategy for correctness, efficiency, and readability
            2. Identify the strongest elements from each approach
            3. Combine the best aspects into a unified solution strategy
            4. Ensure all edge cases from requirements are addressed
            5. Verify the approach matches the expected function signature
            6. Optimize for both correctness and code quality
            
            Provide the final synthesized strategy with clear implementation steps.""",
            contexts_list=strategies
        )
        
        # Phase 3: Code Implementation with Iterative Refinement
        max_attempts = 3
        code_solution = None
        validation_feedback = ""
        
        for attempt in range(max_attempts):
            if attempt == 0:
                # First attempt: Generate code based on selected strategy
                code_context = selected_strategy
            else:
                # Subsequent attempts: Revise based on feedback
                code_context = await self.revise(
                    instruction=f"""Revise the code solution based on this feedback: {validation_feedback}
                    
                    Key requirements to address:
                    {requirements}
                    
                    Maintain the core approach from: {selected_strategy}
                    
                    Fix identified issues while preserving working functionality.
                    Ensure proper handling of all edge cases.
                    Match exact function signature and return type requirements.""",
                    context=code_solution if code_solution else selected_strategy
                )
            
            # Generate code implementation
            code_attempt = await self.programmer(
                instruction=f"""Implement the solution according to this strategy: {code_context}
                
                Requirements to follow:
                {requirements}
                
                Implementation guidelines:
                - Use exact function name and parameters specified
                - Handle all identified edge cases
                - Return correct data type
                - Include necessary imports
                - Write clean, readable code
                - Follow Python best practices
                - Do not include test cases or print statements
                - Return only the function implementation as specified
                
                Generate only the function code, nothing else.""",
                context=code_context,
                max_retries=1
            )
            
            # Extract just the code portion (in case programmer returns additional text)
            code_lines = []
            in_code = False
            for line in code_attempt.split('\n'):
                if line.strip().startswith('