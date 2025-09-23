# Workflow ID: mbppplus_167_0
# Benchmark: mbppplus
# Data Indices: [12, 199]

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

        # PHASE 1: PARALLEL PROBLEM INTERPRETATION
        # Generate three complementary interpretations of the problem
        interpretation_tasks = [
            self.generate(
                instruction="""Analyze the problem from a DATA STRUCTURE perspective:
                - Identify input data types (list, tuple, dict, string, etc.)
                - Identify output data types
                - Note any nesting or hierarchical structures
                - Specify if order must be preserved
                - Highlight any type conversion requirements
                Provide a structured summary focusing on data anatomy.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from a TRANSFORMATION LOGIC perspective:
                - What operation is being performed? (filter, map, reduce, search, etc.)
                - What are the input-to-output transformation rules?
                - Are there conditional branches in the logic?
                - Is recursion or iteration required?
                - What are the termination conditions?
                Provide a step-by-step logical breakdown.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an EDGE CASE & ROBUSTNESS perspective:
                - What are the boundary conditions? (empty inputs, single elements, max/min values)
                - What invalid inputs might occur? How should they be handled?
                - Are there type mismatches to guard against?
                - What performance constraints might exist?
                - What are the failure modes?
                Provide a comprehensive edge case analysis.""",
                context=""
            )
        ]
        
        interpretations = await asyncio.gather(*interpretation_tasks)
        
        # PHASE 2: SYNTHESIZE MASTER SPECIFICATION
        master_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified, comprehensive problem specification:
            - Combine data structure requirements with transformation logic
            - Integrate edge case handling into the core logic
            - Resolve any contradictions between interpretations
            - Produce a single, unambiguous specification that includes:
              1. Input format and constraints
              2. Output format and requirements
              3. Core transformation algorithm
              4. Edge case handling strategy
              5. Type consistency rules
            The output should be detailed enough to guide precise code generation.""",
            contexts_list=interpretations
        )

        # PHASE 3: DYNAMIC CODE GENERATION WITH CONTEXTUAL CONSTRAINTS
        # Check if regex is needed based on master spec
        needs_regex = "space" in master_spec.lower() or "whitespace" in master_spec.lower() or "pattern" in master_spec.lower()
        
        code_instruction = f"""Generate a Python function that solves the problem according to this specification:
        {master_spec}
        
        Additional requirements:
        - Use the EXACT function name and signature from the reference
        - Handle all edge cases mentioned in the specification
        - Return the correct data type (list, tuple, set, etc.) as specified
        - Include necessary imports at the top of the function (e.g., 'import re' if regex is needed)
        - Write clean, efficient code with appropriate variable names
        - Use list comprehensions or generator expressions where appropriate
        - Do not include any test cases or print statements
        - The function must be self-contained and require no external context
        
        {'IMPORTANT: This problem involves string pattern matching - include "import re" at the top.' if needs_regex else ''}
        
        Return ONLY the function implementation, nothing else.
        """

        code_attempt = await self.programmer(
            instruction=code_instruction,
            context=master_spec,
            max_retries=2
        )

        # PHASE 4: VALIDATION AND REFINEMENT LOOP
        validation_instruction = f"""Critically evaluate this code implementation against the problem specification:
        Specification: {master_spec}
        
        Check for:
        - Correct function signature and name
        - Proper handling of edge cases
        - Correct return type and structure
        - Logical correctness of transformation
        - Presence of required imports
        - Code efficiency and readability
        - Any potential bugs or oversights
        
        If issues are found, provide specific, actionable revision instructions.
        If no issues are found, respond with 'VALIDATED: No issues found'."""

        validation = await self.generate(
            instruction=validation_instruction,
            context=code_attempt
        )

        # If validation finds issues, revise the code
        if "VALIDATED" not in validation and "No issues found" not in validation:
            code_attempt = await self.revise(
                instruction=f"""Revise the code to fix the issues identified in the validation:
                Validation feedback: {validation}
                
                Maintain all original requirements from the specification:
                {master_spec}
                
                Return ONLY the corrected function implementation, nothing else.""",
                context=code_attempt
            )

        # PHASE 5: FINAL SANITY CHECK AND OUTPUT
        # Extract just the function code (in case programmer returned additional text)
        final_code = await self.generate(
            instruction="""Extract ONLY the Python function implementation from the following text.
            Remove any explanatory text, markdown formatting, or additional commentary.
            Return ONLY the pure Python code, including imports if present.
            The function must be ready to execute as-is.""",
            context=code_attempt
        )

        return final_code