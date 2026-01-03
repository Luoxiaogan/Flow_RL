# Workflow ID: mbppplus_33_0
# Benchmark: mbppplus
# Data Indices: [259, 133, 218]

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
        import json

        # Phase 1: Multi-Angle Problem Interpretation (Diamond Pattern)
        interpretation_tasks = [
            self.generate(
                instruction="""Analyze the problem from a TYPE CONTRACT perspective:
                - What are the exact input parameter types and constraints?
                - What is the required return type and structure?
                - Are there mutability or side-effect requirements?
                - Extract any implicit type conversion rules.
                Format as structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an EDGE CASE perspective:
                - What are the minimal/empty input scenarios?
                - What are the maximum/boundary value cases?
                - Are there type-mixed or malformed input possibilities?
                - What constitutes 'invalid' input if any?
                List concrete examples of edge cases to test.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an ALGORITHMIC PATTERNS perspective:
                - What computational patterns are suggested (e.g., cumulative, sliding window, run-length, regex)?
                - Are there mathematical properties or invariants to exploit?
                - What is the expected time/space complexity?
                - Are there standard library functions that could be relevant?
                Describe the most suitable algorithmic approach.""",
                context=""
            )
        ]
        
        interpretations = await asyncio.gather(*interpretation_tasks)
        
        # Synthesize interpretations into unified problem model
        problem_model = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem specification:
            - Combine type contracts, edge cases, and algorithmic approaches
            - Resolve any contradictions between analyses
            - Prioritize requirements by criticality
            - Output a comprehensive, structured problem breakdown that captures all constraints and intentions.
            Format as JSON with keys: "type_contract", "edge_cases", "algorithmic_approach", "critical_constraints".""",
            contexts_list=interpretations
        )

        # Phase 2: Dynamic Strategy Classification & Routing
        strategy_classification = await self.generate(
            instruction=f"""Classify this problem based on the synthesized model:
            {problem_model}
            
            Choose ONE primary strategy archetype:
            A) STATE_MACHINE (for sequential processing with memory, e.g., run-length encoding)
            B) CUMULATIVE_COMPUTATION (for problems with overlapping subproblems, e.g., subarray products)
            C) VALIDATION_SCANNER (for pattern matching or filtering, e.g., regex checks)
            D) TRANSFORMATION_PIPELINE (for element-wise operations)
            E) SEARCH_OPTIMIZATION (for problems requiring min/max or existence checks)
            
            Justify your choice by mapping problem characteristics to archetype strengths.
            Output format: "ARCHETYPE: [letter] - [justification]".""",
            context=problem_model
        )

        # Phase 3: Adaptive Implementation Generation with Feedback Loop
        implementation = None
        max_iterations = 3
        
        for iteration in range(max_iterations):
            if iteration == 0:
                # Generate initial implementation
                implementation = await self.generate(
                    instruction=f"""Generate a Python function implementation based on:
                    Problem Model: {problem_model}
                    Strategy: {strategy_classification}
                    
                    Requirements:
                    - Match the exact function signature from the problem
                    - Handle all edge cases identified in the model
                    - Use the classified strategy archetype appropriately
                    - Include necessary imports inside the function if needed
                    - Return exactly the specified type (list/tuple/set)
                    - No print statements or interactive elements
                    - Defensive coding for unexpected inputs
                    
                    Output ONLY the function code, nothing else.""",
                    context=""
                )
            else:
                # Validate and revise
                validator_feedback = await self.generate(
                    instruction=f"""Critique this implementation for robustness:
                    {implementation}
                    
                    Specifically check:
                    - Does it handle ALL edge cases from the problem model?
                    - Are there type mismatches or return format errors?
                    - Are there logical flaws in the algorithmic approach?
                    - Could it fail on boundary conditions?
                    - Is it unnecessarily complex or inefficient?
                    
                    Provide specific, actionable revision instructions.
                    If no issues found, respond with 'VALIDATED'.""",
                    context=implementation
                )
                
                if "VALIDATED" in validator_feedback.upper():
                    break
                    
                implementation = await self.revise(
                    instruction=f"""Revise the implementation based on this feedback:
                    {validator_feedback}
                    
                    Also ensure:
                    - Function signature is preserved exactly
                    - All edge cases from problem model are handled
                    - Code remains clean and readable
                    - No new bugs are introduced
                    
                    Output ONLY the revised function code.""",
                    context=implementation
                )

        # Phase 4: Final Contract Verification
        contract_verification = await self.summarize(
            instruction=f"""Verify this implementation against the original problem's contractual requirements:
            Implementation: {implementation}
            Problem Model: {problem_model}
            
            Check:
            - Does the function name match exactly?
            - Are parameter names and order preserved?
            - Is the return type and structure correct?
            - Are all edge cases from the model addressed?
            - Are there any extraneous outputs or side effects?
            
            If any mismatch, output revision instructions.
            If perfect match, output 'CONTRACT_FULFILLED'.""",
            context=implementation
        )

        if "CONTRACT_FULFILLED" not in contract_verification:
            implementation = await self.revise(
                instruction=f"""Final revision based on contract verification:
                {contract_verification}
                
                This is the last chance to fix any remaining issues.
                Output ONLY the final function code.""",
                context=implementation
            )

        return implementation