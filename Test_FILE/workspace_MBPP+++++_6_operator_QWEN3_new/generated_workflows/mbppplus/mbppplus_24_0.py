# Workflow ID: mbppplus_24_0
# Benchmark: mbppplus
# Data Indices: [284, 193]

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
        import json

        # Phase 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its fundamental components:
            1. Identify input types and constraints (e.g., string, list, integer, etc.)
            2. Specify exact output type and format requirements
            3. List all edge cases that must be handled (empty inputs, single elements, duplicates, boundary values)
            4. Determine if order matters, if duplicates should be preserved, or if type conversion is needed
            5. Identify algorithmic patterns that might apply (e.g., mapping, filtering, searching, regex, mathematical operations)
            6. Note any explicit or implicit constraints from the problem description
            Return structured subproblems that will guide solution generation.""",
            context=""
        )

        # Phase 2: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Propose a solution strategy focusing on ALGORITHMIC PURITY:
                - Use core data structures (dicts, sets, lists) without external libraries
                - Emphasize time/space efficiency
                - Handle all edge cases identified in decomposition: {json.dumps(decomposition)}
                - Ensure type consistency and signature compliance
                Describe the approach step by step.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a solution strategy focusing on BUILT-IN PYTHON FEATURES:
                - Leverage standard library modules (re, itertools, collections, etc.) where appropriate
                - Prioritize readability and maintainability
                - Handle all edge cases: {json.dumps(decomposition)}
                - Match exact function signature and return type
                Describe the approach with code structure hints.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a solution strategy focusing on ROBUSTNESS AND DEFENSIVE PROGRAMMING:
                - Include explicit input validation
                - Handle type coercion and error cases gracefully
                - Add inline comments for clarity
                - Cover edge cases comprehensively: {json.dumps(decomposition)}
                - Ensure backward compatibility with basic test cases
                Describe with emphasis on failure mode prevention.""",
                context=""
            )
        ]
        
        strategies = await asyncio.gather(*strategy_tasks)

        # Phase 3: Generate code candidates based on each strategy
        code_tasks = [
            self.programmer(
                instruction=f"""Generate a complete Python function implementation based on this strategy:
                {strategy}
                
                STRICT REQUIREMENTS:
                - Use EXACT function name and signature from problem
                - Include ALL necessary imports INSIDE the function if needed
                - Handle ALL edge cases from decomposition: {json.dumps(decomposition)}
                - Return correct data type (bool, list, tuple, string, etc.)
                - Pass all basic test cases shown in problem
                - Write defensive code that won't break on unexpected inputs
                - No outer wrappers, classes, or additional functions
                - Code must be production-ready and efficient""",
                context="",
                max_retries=2
            ) for strategy in strategies
        ]
        
        code_candidates = await asyncio.gather(*code_tasks)

        # Phase 4: Validate each candidate against anticipated edge cases
        validation_tasks = [
            self.generate(
                instruction=f"""Critically evaluate this code for robustness:
                {code}
                
                CHECKLIST:
                1. Does it handle empty inputs?
                2. Does it handle single-element cases?
                3. Does it handle type mismatches or invalid inputs gracefully?
                4. Does it preserve required data types (list vs tuple vs set)?
                5. Does it maintain order when required?
                6. Does it handle duplicates correctly?
                7. Does it match the exact function signature?
                8. Are there any obvious edge cases it would fail on?
                
                Return detailed critique with specific improvement suggestions if needed.""",
                context=code
            ) for code in code_candidates
        ]
        
        validations = await asyncio.gather(*validation_tasks)

        # Phase 5: Revise candidates based on validation feedback
        revised_candidates = []
        for i, (code, validation) in enumerate(zip(code_candidates, validations)):
            if "fail" in validation.lower() or "error" in validation.lower() or "missing" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Improve this code based on the validation feedback:
                    {validation}
                    
                    REQUIRED IMPROVEMENTS:
                    - Fix all identified issues
                    - Maintain original function signature
                    - Preserve core logic while adding robustness
                    - Ensure all edge cases are handled
                    - Keep code clean and efficient""",
                    context=code
                )
                revised_candidates.append(revised)
            else:
                revised_candidates.append(code)

        # Phase 6: Ensemble synthesis - select or merge the best solution
        final_code = await self.ensemble(
            instruction="""Select the single best solution from these candidates:
            CRITERIA:
            1. Correctness (must handle all edge cases)
            2. Efficiency (time and space complexity)
            3. Readability and maintainability
            4. Adherence to function signature and type requirements
            5. Defensive programming and error handling
            6. Simplicity (avoid over-engineering)
            
            If multiple candidates are equally strong, synthesize the best elements from each.
            Return ONLY the final code implementation with necessary imports, nothing else.""",
            contexts_list=revised_candidates
        )

        return final_code