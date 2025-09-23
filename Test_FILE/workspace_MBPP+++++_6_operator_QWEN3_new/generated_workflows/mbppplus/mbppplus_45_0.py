# Workflow ID: mbppplus_45_0
# Benchmark: mbppplus
# Data Indices: [194, 116]

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

        # Step 1: Decompose the problem into structured subproblems
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into essential subproblems with clear dependencies. Focus on:
            1. Input structure and type (list, dict, tuple, etc.)
            2. Output requirements and type signature
            3. Core algorithmic or mathematical operation needed
            4. Edge cases (empty input, single element, boundary values)
            5. Performance or efficiency constraints if any
            6. Any implicit constraints from test cases
            Return each subproblem with a unique ID and dependencies on other subproblems.""",
            context=""
        )

        # Step 2: Parallel analysis - explore multiple solution angles
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on problem decomposition:
                {json.dumps(decomposition, indent=2)}
                
                Develop a mathematical/formula-based solution strategy. Focus on:
                - Deriving any necessary formulas or equations
                - Identifying computational steps
                - Handling numerical precision if applicable
                - Mathematical edge cases (division by zero, empty sets, etc.)""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on problem decomposition:
                {json.dumps(decomposition, indent=2)}
                
                Develop a data structure/algorithmic solution strategy. Focus on:
                - Appropriate data structures (lists, heaps, sets, etc.)
                - Algorithm selection (sorting, filtering, searching, etc.)
                - Time/space complexity considerations
                - Structural edge cases (empty collections, type mismatches)""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on problem decomposition:
                {json.dumps(decomposition, indent=2)}
                
                Extract and formalize all edge cases and boundary conditions. For each:
                - Describe the scenario (e.g., empty input, n=0, single element)
                - Specify expected behavior based on problem context
                - Note any type consistency requirements
                Format as a numbered list with clear scenario→behavior mapping.""",
                context=""
            )
        ]
        
        math_strategy, data_strategy, edge_cases = await asyncio.gather(*strategy_tasks)

        # Step 3: Ensemble synthesis - merge strategies into coherent plan
        synthesized_plan = await self.ensemble(
            instruction="""Synthesize the three solution perspectives into one unified implementation plan. Prioritize:
            1. Correctness for all identified edge cases
            2. Type consistency with expected return types
            3. Algorithmic efficiency where applicable
            4. Code simplicity and readability
            5. Alignment with Python best practices
            Explicitly resolve any conflicts between strategies (e.g., if math approach suggests one formula but data approach suggests different algorithm).
            Output should be a step-by-step implementation guide including:
            - Required imports
            - Function structure
            - Key algorithmic steps
            - Edge case handling logic
            - Return type enforcement""",
            contexts_list=[math_strategy, data_strategy, edge_cases]
        )

        # Step 4: Initial code generation
        first_attempt = await self.programmer(
            instruction=f"""Implement the function exactly as specified in the original problem. Use this implementation plan:
            {synthesized_plan}
            
            CRITICAL REQUIREMENTS:
            - Use EXACT function name and parameters from original problem
            - Include all necessary imports at top of function
            - Return correct data type (list vs tuple vs set) as implied by test cases
            - Handle ALL edge cases identified in plan
            - Code must be syntactically valid Python
            - Do NOT include any test code or print statements
            - Return only the function implementation as string""",
            context=synthesized_plan
        )

        # Step 5: Iterative refinement loop (max 2 iterations)
        current_code = first_attempt
        for iteration in range(2):
            # Simulate edge case testing
            edge_case_validation = await self.generate(
                instruction=f"""Analyze this code for edge case robustness:
                {current_code}
                
                Based on previously identified edge cases:
                {edge_cases}
                
                Identify any gaps or failures in handling these cases. Be specific:
                - Which edge case is not handled?
                - What would happen when that case is encountered?
                - What code change is needed to fix it?
                If no issues found, respond 'NO ISSUES FOUND'.""",
                context=current_code
            )
            
            if "NO ISSUES FOUND" in edge_case_validation.upper():
                break
                
            # Revise code to fix edge case issues
            current_code = await self.revise(
                instruction=f"""Revise the code to fix the following edge case issues:
                {edge_case_validation}
                
                PRESERVE:
                - Original function signature
                - Core algorithmic logic
                - Type consistency
                - Code readability
                
                ADD:
                - Missing edge case handling
                - Defensive checks where needed
                - Clear comments for complex logic
                
                Return only the complete revised function implementation.""",
                context=current_code
            )

        # Step 6: Final type and signature enforcement
        final_code = await self.revise(
            instruction=f"""Ensure this code strictly matches the original problem's requirements:
            {current_code}
            
            VERIFY AND ENFORCE:
            1. Function name and parameters exactly match original
            2. Return type consistency (if tests show list, return list; if tuple, return tuple)
            3. No unnecessary imports or code outside function
            4. Proper handling of all edge cases
            5. Clean, idiomatic Python style
            
            Make minimal changes only to enforce these requirements. Return complete function implementation.""",
            context=current_code
        )

        return final_code