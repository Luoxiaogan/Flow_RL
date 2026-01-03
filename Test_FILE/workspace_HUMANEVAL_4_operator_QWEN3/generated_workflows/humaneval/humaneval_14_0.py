# Workflow ID: humaneval_14_0
# Benchmark: humaneval
# Data Indices: [105, 113]

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

    async def run_workflow(self):
        import asyncio
        import re
        
        # Phase 1: Parallel analysis - extract different perspectives
        classification_task = self.generate(
            instruction="""Analyze the problem and classify it by type. Consider:
            - What kind of data transformations are involved? (string, numeric, list, etc.)
            - What are the key operations? (sorting, filtering, mapping, counting, etc.)
            - What are the edge cases mentioned or implied?
            - What is the exact output format required?
            Provide a structured analysis covering these aspects.""",
            context=""
        )
        
        example_extraction_task = self.generate(
            instruction="""Extract all examples from the docstring. For each example:
            - Identify the input
            - Identify the expected output
            - Note any transformation steps described
            - Highlight any special conditions or edge cases
            Present as a structured list of input-output pairs with annotations.""",
            context=""
        )
        
        edge_case_analysis_task = self.generate(
            instruction="""Identify all edge cases from the problem description and examples. Consider:
            - Empty inputs
            - Invalid inputs
            - Boundary values
            - Special conditions mentioned
            - Any "ignore" or "filter" requirements
            List each edge case with the expected behavior.""",
            context=""
        )
        
        # Execute parallel analysis
        classification, examples, edge_cases = await asyncio.gather(
            classification_task, 
            example_extraction_task, 
            edge_case_analysis_task
        )
        
        # Phase 2: Synthesize comprehensive specification
        specification = await self.ensemble(
            instruction="""Synthesize a comprehensive code specification from the three analyses. The specification must include:
            1. Function signature (exact name from ENTRY POINT)
            2. Input parameter description
            3. Step-by-step transformation logic
            4. Edge case handling requirements
            5. Exact output format
            6. Any constraints or limitations
            Be extremely precise - this will be used to generate code that must pass hidden tests.
            Format as a detailed, unambiguous specification document.""",
            contexts_list=[classification, examples, edge_cases]
        )
        
        # Phase 3: Generate initial code implementation
        initial_code = await self.generate(
            instruction=f"""Generate Python code that implements the following specification exactly:
            {specification}
            
            Requirements:
            - Use the exact function name specified in ENTRY POINT
            - Match the return type and format exactly as shown in examples
            - Handle all edge cases identified
            - No additional functionality beyond what's specified
            - Return only the code, no explanations or markdown
            - Include necessary logic but keep it minimal and focused
            
            Think step by step:
            1. Parse the specification
            2. Implement core transformation logic
            3. Add edge case handling
            4. Verify output format matches examples
            5. Return only the raw Python code""",
            context=specification
        )
        
        # Phase 4: Iterative self-validation and refinement
        current_code = initial_code
        max_iterations = 3
        
        for iteration in range(max_iterations):
            # Validate against examples
            validation = await self.generate(
                instruction=f"""Validate this code against the problem specification and examples:
                Code to validate:
                {current_code}
                
                Specification:
                {specification}
                
                Perform step-by-step validation:
                1. For each example in the specification, simulate what the code would output
                2. Compare with expected output
                3. Identify any discrepancies
                4. Check edge case handling
                5. Verify function name and signature
                6. Confirm return type and format
                
                If perfect match, respond with "VALID: [brief confirmation]".
                If any issues, respond with "INVALID: [detailed description of issues]". Be specific about what's wrong.""",
                context=current_code
            )
            
            if "VALID:" in validation:
                break
            else:
                # Revise code based on validation feedback
                current_code = await self.revise(
                    instruction=f"""Revise the code to fix the issues identified in validation:
                    Validation feedback:
                    {validation}
                    
                    Original specification:
                    {specification}
                    
                    Requirements:
                    - Fix all identified issues
                    - Maintain exact function signature
                    - Preserve correct behavior for all examples
                    - Return only the raw Python code, no explanations
                    - Be precise and minimal""",
                    context=current_code
                )
        
        # Final cleanup - ensure only code is returned
        final_code = await self.generate(
            instruction="""Extract only the Python code from the following text. Remove any explanations, markdown, or non-code text.
            Return exactly the code that should be executed, nothing else.
            Ensure the function name matches ENTRY POINT exactly.
            If there are multiple code blocks, return only the main function implementation.""",
            context=current_code
        )
        
        return final_code