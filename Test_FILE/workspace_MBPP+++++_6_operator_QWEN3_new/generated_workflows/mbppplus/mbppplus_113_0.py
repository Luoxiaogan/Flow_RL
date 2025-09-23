# Workflow ID: mbppplus_113_0
# Benchmark: mbppplus
# Data Indices: [6, 274]

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

        # STEP 1: CLASSIFY THE PROBLEM TYPE AND STRUCTURE
        classification = await self.generate(
            instruction="""Thoroughly analyze the problem and classify it with extreme precision. Your output must be a JSON object with these keys:
            - "problem_type": One of ["string_pattern", "mathematical_computation", "data_structure_operation", "logical_validation"]
            - "input_types": List of expected input types (e.g., ["str", "str"] or ["list[tuple[int,int]]"])
            - "output_type": Expected return type (e.g., "tuple", "int", "list")
            - "edge_cases": List of predicted edge cases (e.g., ["empty string", "single element", "duplicates"])
            - "requires_decomposition": Boolean indicating if problem should be broken into subproblems
            - "key_operations": List of core operations needed (e.g., ["regex search", "absolute difference", "min reduction"])
            
            Base your analysis on the function signature, test cases, and problem description. Be exhaustive and precise.""",
            context=""
        )

        # Parse classification
        try:
            class_data = json.loads(classification)
        except:
            # Fallback classification if JSON fails
            class_data = {
                "problem_type": "mathematical_computation",
                "input_types": ["list"],
                "output_type": "int",
                "edge_cases": ["empty list"],
                "requires_decomposition": True,
                "key_operations": ["iterate", "compute", "compare"]
            }

        # STEP 2: CONDITIONAL DECOMPOSITION
        subproblems = []
        if class_data.get("requires_decomposition", False):
            try:
                subproblems = await self.decompose(
                    instruction=f"""Decompose this {class_data['problem_type']} problem into atomic, executable subproblems. 
                    Each subproblem should be independently solvable and have clear input/output. 
                    Respect dependencies: if step B needs step A's output, mark A as dependency.
                    Focus on the key operations: {', '.join(class_data['key_operations'])}
                    Consider edge cases: {', '.join(class_data['edge_cases'])}""",
                    context=""
                )
            except:
                subproblems = []

        # STEP 3: PARALLEL SOLUTION GENERATION (DIAMOND PATTERN)
        solution_approaches = [
            """Generate a CORRECTNESS-FIRST solution. Prioritize:
            - Exact adherence to function signature
            - Type safety and consistency
            - Direct implementation of specified behavior
            - Minimal assumptions about input
            Return ONLY the function implementation as code, no explanations.""",
            
            """Generate a ROBUSTNESS-FIRST solution. Prioritize:
            - Handling all edge cases: {edge_cases}
            - Defensive programming: validate inputs, handle exceptions
            - Comprehensive test coverage in code logic
            - Graceful degradation on invalid inputs
            Return ONLY the function implementation as code, no explanations.""".format(edge_cases=class_data['edge_cases']),
            
            """Generate a CLARITY-FIRST solution. Prioritize:
            - Readable, self-documenting code
            - Meaningful variable names
            - Logical flow that matches problem description
            - Comments only if essential for understanding
            Return ONLY the function implementation as code, no explanations."""
        ]

        solution_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in solution_approaches]
        )

        # STEP 4: ENSEMBLE SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize a FINAL SOLUTION by combining the best elements from all candidates:
            - Take CORRECTNESS from candidate 1
            - Take ROBUSTNESS from candidate 2
            - Take CLARITY from candidate 3
            - Ensure output type matches: {class_data['output_type']}
            - Handle edge cases: {', '.join(class_data['edge_cases'])}
            - Preserve function signature exactly
            
            Return ONLY the final function implementation as clean Python code, no explanations or markdown.""",
            contexts_list=solution_candidates
        )

        # STEP 5: VALIDATION & REFINEMENT LOOP
        final_code = synthesized_solution
        for attempt in range(3):
            try:
                validation_result = await self.programmer(
                    instruction=f"""Execute this code against comprehensive test cases including:
                    - Normal cases from problem description
                    - Edge cases: {', '.join(class_data['edge_cases'])}
                    - Type boundary cases
                    - Performance stress tests (if applicable)
                    
                    If errors occur, return detailed error messages. If successful, return 'VALID'.
                    The code must be production-ready and handle all specified cases.""",
                    context=final_code,
                    max_retries=1
                )
                
                if "VALID" in validation_result.upper() or "ERROR" not in validation_result.upper():
                    break
                else:
                    # Revise based on errors
                    final_code = await self.revise(
                        instruction=f"""Fix all errors identified in validation:
                        {validation_result}
                        
                        Maintain:
                        - Correctness of core logic
                        - Robustness against edge cases
                        - Clarity of implementation
                        - Exact function signature
                        
                        Return ONLY the corrected function implementation.""",
                        context=final_code
                    )
            except Exception as e:
                # Final revision attempt with error context
                final_code = await self.revise(
                    instruction=f"""Critical fix needed due to execution failure:
                    {str(e)}
                    
                    Reimplement with extreme caution for:
                    - Type safety
                    - Boundary conditions
                    - Exception handling
                    - Signature compliance
                    
                    Return ONLY the corrected function implementation.""",
                    context=final_code
                )

        return final_code