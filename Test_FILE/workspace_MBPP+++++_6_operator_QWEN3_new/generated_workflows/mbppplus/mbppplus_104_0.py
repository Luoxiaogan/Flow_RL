# Workflow ID: mbppplus_104_0
# Benchmark: mbppplus
# Data Indices: [347, 342]

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
        import json

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into fundamental subproblems. For each subproblem, specify:
            - The exact operation or transformation required
            - Input and output data types
            - Edge cases to consider (empty inputs, single elements, duplicates, boundary conditions)
            - Whether order, mutability, or uniqueness matters
            - Any implicit constraints from the test cases
            Format each subproblem as a clear, standalone description with dependencies if any.""",
            context=""
        )

        # Step 2: Parallel analysis branches
        type_analysis_task = self.generate(
            instruction="""Analyze the type system requirements:
            - What are the exact input parameter types (list, tuple, set, string, etc.)?
            - What is the required return type?
            - Are there any type conversion requirements?
            - Does the solution need to preserve order or handle duplicates?
            - What Python built-in functions or behaviors are relevant?
            Output as a structured summary with clear type signatures.""",
            context=""
        )

        strategy_analysis_task = self.generate(
            instruction="""Generate 3 distinct solution strategies:
            1. A direct, naive approach
            2. An optimized or idiomatic Python approach
            3. A defensive, edge-case-heavy approach
            For each, outline the algorithmic steps, time complexity, and potential failure points.
            Prioritize approaches that match the test case patterns shown.""",
            context=""
        )

        edge_case_analysis_task = self.generate(
            instruction="""Identify all potential edge cases:
            - Empty inputs
            - Single element inputs
            - Boundary indices (0, -1, len, -len)
            - Duplicate elements
            - Type mismatches
            - Invalid indices or values
            For each edge case, specify how the function should behave (raise error, return default, etc.)
            Cross-reference with any test cases provided.""",
            context=""
        )

        # Execute parallel analyses
        type_analysis, strategy_analysis, edge_case_analysis = await asyncio.gather(
            type_analysis_task, strategy_analysis_task, edge_case_analysis_task
        )

        # Step 3: Ensemble - Synthesize into unified specification
        specification = await self.ensemble(
            instruction="""Synthesize all analyses into a single, comprehensive specification:
            1. Function signature with exact parameter and return types
            2. Chosen solution strategy (select the most robust and idiomatic)
            3. Complete edge case handling protocol
            4. Validation criteria (what constitutes a correct solution)
            5. Any necessary imports or Python version considerations
            Resolve conflicts by prioritizing test case evidence and Python best practices.
            Format as a clear, structured document that can guide code generation.""",
            contexts_list=[type_analysis, strategy_analysis, edge_case_analysis]
        )

        # Step 4: Generate implementation plan (pseudocode)
        implementation_plan = await self.generate(
            instruction=f"""Based on this specification:
            {specification}
            
            Create a detailed, line-by-line implementation plan in pseudocode. Include:
            - Variable initialization
            - Core algorithm steps
            - Edge case handling branches
            - Return statement
            - Any necessary error handling
            Do not write actual Python code yet — focus on logic structure.""",
            context=specification
        )

        # Step 5: Revise plan into precise implementation blueprint
        blueprint = await self.revise(
            instruction="""Convert this pseudocode plan into a precise Python implementation blueprint:
            - Replace pseudocode with actual Python syntax
            - Add specific function signature from specification
            - Include all necessary imports at top
            - Handle every edge case explicitly
            - Use defensive programming (e.g., try-except only if specified)
            - Ensure return type matches specification exactly
            Output should be ready for direct code generation.""",
            context=implementation_plan
        )

        # Step 6: Generate code with validation
        code_attempt = await self.programmer(
            instruction=f"""Generate Python code based on this blueprint:
            {blueprint}
            
            Validate against these edge cases:
            {edge_case_analysis}
            
            Requirements:
            - Include all necessary imports
            - Match function signature exactly
            - Handle all specified edge cases
            - Return correct data type
            - No extra text or explanations — only code""",
            context=blueprint,
            max_retries=1
        )

        # Step 7: Validation loop (up to 3 iterations)
        final_code = code_attempt
        for attempt in range(3):
            validator_feedback = await self.generate(
                instruction=f"""Validate this code against the problem requirements:
                {final_code}
                
                Check for:
                - Correct function signature
                - Proper handling of all edge cases
                - Correct return type
                - No unnecessary imports or code
                - Matches test case behavior
                If any issues found, describe them specifically. If perfect, respond with 'PASSED'.""",
                context=final_code
            )
            
            if "PASSED" in validator_feedback.upper():
                break
                
            # Revise based on feedback
            final_code = await self.revise(
                instruction=f"""Fix all issues identified in this feedback:
                {validator_feedback}
                
                Preserve the core logic but correct the specific problems.
                Ensure the code still matches the original specification.
                Return only the corrected Python code.""",
                context=final_code
            )
        else:
            # Fallback: Try alternative approach if still failing
            alternative_approach = await self.generate(
                instruction=f"""Previous attempts failed. Try a completely different approach:
                Original specification: {specification}
                Last code: {final_code}
                Last feedback: {validator_feedback}
                
                Consider set operations, recursion, or built-in functions not previously used.
                Generate a fresh implementation from scratch.""",
                context=""
            )
            
            final_code = await self.programmer(
                instruction=f"""Generate code using this alternative approach:
                {alternative_approach}
                
                Follow all original requirements and edge case handling.
                Return only the Python function implementation.""",
                context=alternative_approach,
                max_retries=1
            )

        # Step 8: Final cleanup - extract only the function code
        clean_code = await self.summarize(
            instruction="""Extract only the final Python function implementation from the following text.
            Remove any explanations, markdown, extra text, or commentary.
            Return ONLY the pure Python code, exactly as it should appear in the final answer.
            Ensure it includes the function signature, body, and any necessary imports.
            Do not add any additional text or formatting.""",
            context=final_code
        )

        return clean_code