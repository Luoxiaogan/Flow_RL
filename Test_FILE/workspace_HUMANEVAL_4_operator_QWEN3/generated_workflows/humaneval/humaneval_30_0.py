# Workflow ID: humaneval_30_0
# Benchmark: humaneval
# Data Indices: [78, 50]

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
        
        # Phase 1: Problem Analysis - Extract key components
        analysis = await self.generate(
            instruction="""Thoroughly analyze the given problem specification. Extract and structure the following:
            1. Function name and signature (must match ENTRY POINT exactly)
            2. Complete docstring including all examples
            3. Identify input/output types from examples
            4. Note any explicit constraints or edge cases mentioned
            5. Infer the core operation: is this counting, transforming, calculating, or filtering?
            6. List the example input-output pairs and look for patterns
            7. Identify any special characters, ranges, or conditions that matter
            Present this as a structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Strategy Generation - Parallel approach generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on the problem analysis:
                {analysis}
                
                Develop a STRATEGY for solving this as a PATTERN MATCHING / COUNTING problem.
                - Identify what elements to count or match
                - Define the set of valid/invalid items
                - Consider iteration approach (string, list, etc.)
                - Handle edge cases like empty input
                - Return type must match examples exactly
                Provide detailed step-by-step strategy.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
                {analysis}
                
                Develop a STRATEGY for solving this as a TRANSFORMATION / INVERSE FUNCTION problem.
                - Identify the forward operation if any (like encoding)
                - Derive the reverse/inverse operation
                - Consider modular arithmetic, character shifts, etc.
                - Handle edge cases like empty input
                - Return type must match examples exactly
                Provide detailed step-by-step strategy.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
                {analysis}
                
                Develop a STRATEGY for solving this as a MATHEMATICAL / FORMULA-BASED problem.
                - Look for numerical patterns in examples
                - Derive potential formulas or algorithms
                - Consider base cases and recursion if applicable
                - Handle edge cases like empty input
                - Return type must match examples exactly
                Provide detailed step-by-step strategy.""",
                context=analysis
            )
        ]
        
        strategies = await asyncio.gather(*strategy_tasks)
        
        # Phase 3: Code Generation - Parallel implementation attempts
        code_tasks = []
        for i, strategy in enumerate(strategies):
            code_tasks.append(
                self.generate(
                    instruction=f"""Implement the solution based on this strategy:
                    {strategy}
                    
                    CRITICAL REQUIREMENTS:
                    - Function name MUST exactly match the ENTRY POINT specified
                    - Return type must match examples precisely (int vs float matters)
                    - Handle all edge cases mentioned in docstring
                    - Code must be minimal and exactly implement what's specified
                    - No extra functionality or over-engineering
                    - Include handling for empty string if mentioned
                    - Use simple, clear Python code
                    Generate ONLY the function implementation, nothing else.""",
                    context=strategy
                )
            )
        
        code_candidates = await asyncio.gather(*code_tasks)
        
        # Phase 4: Ensemble Selection - Choose best implementation
        selected_code = await self.ensemble(
            instruction="""Evaluate these candidate implementations and select the BEST one:
            - Must exactly match function signature from specification
            - Must handle all edge cases mentioned
            - Must have correct return type
            - Should be simplest and most direct implementation
            - Should match the pattern shown in examples
            - Avoid over-engineered or unnecessarily complex solutions
            Return ONLY the selected code, nothing else.""",
            contexts_list=code_candidates
        )
        
        # Phase 5: Final Revision - Ensure perfection
        final_code = await self.revise(
            instruction="""Critically review this code and make final improvements:
            1. Verify function name exactly matches ENTRY POINT
            2. Check return type matches all examples
            3. Ensure edge cases (like empty string) are handled
            4. Simplify if possible - remove any unnecessary complexity
            5. Ensure no imports are needed (problem states they'll be auto-added)
            6. Format as clean, idiomatic Python
            7. Return ONLY the function code, nothing else""",
            context=selected_code
        )
        
        return final_code