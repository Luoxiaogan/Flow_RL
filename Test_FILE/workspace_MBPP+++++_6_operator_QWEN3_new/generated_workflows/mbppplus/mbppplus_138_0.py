# Workflow ID: mbppplus_138_0
# Benchmark: mbppplus
# Data Indices: [131, 10]

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

        # Phase 1: Parallel Problem Analysis
        semantic_analysis = self.generate(
            instruction="""Deeply analyze the problem's semantic intent. 
            What is the core transformation or computation being requested? 
            Identify the 'verb' of the problem (e.g., 'find', 'replace', 'filter', 'compute'). 
            What real-world analogy fits this task? 
            What would a non-programmer expect as output?""",
            context=""
        )
        
        type_analysis = self.generate(
            instruction="""Infer all data types and structures involved. 
            What is the input type? (string, list, tuple, nested structure) 
            What is the expected output type? 
            Are there type conversion requirements? 
            Must order be preserved? Are duplicates allowed? 
            What Python built-ins or standard library modules are likely needed?""",
            context=""
        )
        
        edge_case_analysis = self.generate(
            instruction="""Identify all potential edge cases and constraints. 
            Consider: empty inputs, single-element inputs, boundary values, 
            negative indices, type mismatches, unicode characters, 
            performance constraints, and ambiguous specifications. 
            What would break a naive implementation?""",
            context=""
        )

        # Wait for all analyses to complete
        analyses = await asyncio.gather(semantic_analysis, type_analysis, edge_case_analysis)
        
        # Phase 2: Synthesize Unified Specification
        synthesized_spec = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, unambiguous problem specification. 
            Include: 
            1. Clear input/output type contracts 
            2. Transformation rules in plain English 
            3. Required edge case handling 
            4. Performance or style constraints 
            5. Any assumptions made to resolve ambiguity 
            Format as a structured markdown document.""",
            contexts_list=analyses
        )

        # Phase 3: Generate Initial Solution
        initial_code = await self.programmer(
            instruction=f"""Generate a Python function that solves the problem according to this specification:
            {synthesized_spec}
            
            Requirements:
            - Use only standard library imports
            - Handle all edge cases identified
            - Return correct data type
            - Include type hints if possible
            - Write clean, readable code
            - Add inline comments for complex logic""",
            context=synthesized_spec,
            max_retries=3
        )

        # Phase 4: Validation and Hardening Loop
        for iteration in range(2):  # Max 2 revision cycles
            # Generate validation report
            validation_report = await self.generate(
                instruction=f"""Critically evaluate this code against the problem specification:
                {synthesized_spec}
                
                Check:
                1. Does it handle all edge cases?
                2. Does it return correct data type?
                3. Is it efficient for large inputs?
                4. Are there any logical flaws?
                5. Does it match the semantic intent?
                
                Return 'PASSED' if perfect, otherwise list specific issues.""",
                context=initial_code
            )
            
            if "PASSED" in validation_report.upper():
                break
                
            # Revise code based on validation
            initial_code = await self.revise(
                instruction=f"""Fix all issues identified in this validation report:
                {validation_report}
                
                Maintain all correct functionality while addressing the flaws.
                Preserve the function signature and return type.
                Add additional test cases as inline assertions if helpful.""",
                context=initial_code
            )

        # Phase 5: Extract and Return Final Code
        final_code = await self.generate(
            instruction="""Extract only the final Python function code from this response. 
            Remove any explanations, markdown formatting, or additional text. 
            Return ONLY the function definition with any necessary imports. 
            Ensure perfect syntax and adherence to the original function signature.""",
            context=initial_code
        )
        
        return final_code