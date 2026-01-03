# Workflow ID: humaneval_62_0
# Benchmark: humaneval
# Data Indices: [159, 148]

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

        # PHASE 1: Problem Analysis & Classification
        analysis = await self.generate(
            instruction="""Perform deep structural analysis of the problem:
            1. Extract the exact function name from the ENTRY POINT section.
            2. Parse all examples from the docstring - for each, extract input parameters and expected output.
            3. Identify the return type (list, tuple, int, etc.) from example outputs.
            4. Extract all constraints and variable descriptions.
            5. Classify the problem type: 
               - Arithmetic/Conditional (like resource allocation)
               - Sequence/Enumeration (like ordered lists or tuples)
               - String/Pattern manipulation
               - Other (specify)
            6. Identify edge cases demonstrated in examples.
            7. Hypothesize the core algorithm from example patterns.
            Format as structured JSON with keys: function_name, examples, return_type, constraints, problem_type, edge_cases, algorithm_hypothesis""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation
        # Generate multiple candidate solutions using different strategies
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate Python code based on this analysis:
                {analysis}
                
                STRATEGY 1: Direct Implementation
                - Implement the most straightforward interpretation of the examples.
                - Use minimal abstractions.
                - Focus on matching example outputs exactly.
                - Return code ONLY - no explanations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate Python code based on this analysis:
                {analysis}
                
                STRATEGY 2: Defensive Implementation
                - Include explicit checks for edge cases mentioned in constraints.
                - Use clear variable names and intermediate steps.
                - Add comments explaining key logic.
                - Return code ONLY - no explanations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate Python code based on this analysis:
                {analysis}
                
                STRATEGY 3: Optimized Implementation
                - Use the most efficient approach (minimal operations, no redundant checks).
                - Leverage Python built-ins and slicing where appropriate.
                - Prioritize readability and conciseness.
                - Return code ONLY - no explanations.""",
                context=analysis
            )
        ]
        
        candidates = await asyncio.gather(*candidate_tasks)

        # PHASE 3: Validation & Refinement
        validation_tasks = []
        for i, candidate in enumerate(candidates):
            validation = await self.generate(
                instruction=f"""Validate this candidate solution against the problem analysis:
                Analysis: {analysis}
                Candidate Code: {candidate}
                
                Perform these checks:
                1. Does the function name match exactly?
                2. Does the return type match the examples (list vs tuple vs int)?
                3. Simulate each example - does output match exactly?
                4. Are all constraints handled?
                5. Are edge cases covered?
                6. Is the code free of imports or external dependencies?
                
                If any issues found, describe them specifically. If perfect, say "VALID".
                Format: "ISSUES: [list] OR VALID""",
                context=candidate
            )
            validation_tasks.append(validation)
        
        # Revise candidates with issues
        revised_candidates = []
        for i, (candidate, validation) in enumerate(zip(candidates, validation_tasks)):
            if "VALID" in validation:
                revised_candidates.append(candidate)
            else:
                revised = await self.revise(
                    instruction=f"""Revise this code to fix the following issues:
                    {validation}
                    
                    Original Analysis: {analysis}
                    Original Code: {candidate}
                    
                    Requirements:
                    - Fix all identified issues
                    - Maintain correct function name
                    - Match return type exactly
                    - Handle all edge cases
                    - Return code ONLY - no explanations""",
                    context=candidate
                )
                revised_candidates.append(revised)

        # PHASE 4: Ensemble Selection
        final_code = await self.ensemble(
            instruction=f"""Select the best solution from these candidates:
            Analysis: {analysis}
            Candidates: {revised_candidates}
            
            Selection Criteria:
            1. Correctness: Must pass all example simulations
            2. Simplicity: Minimal, readable code
            3. Robustness: Handles edge cases explicitly
            4. Type Compliance: Return type matches examples exactly
            5. No over-engineering: Implements only what's specified
            
            Return ONLY the selected code - no explanations or markdown.""",
            contexts_list=revised_candidates
        )

        # PHASE 5: Final Sanitization
        # Ensure code is clean and matches exact requirements
        sanitized_code = await self.revise(
            instruction="""Final sanitization pass:
            - Remove any comments or print statements
            - Ensure function name matches ENTRY POINT exactly
            - Verify return type matches examples (list, tuple, etc.)
            - Remove any unnecessary whitespace or formatting
            - Return ONLY the function definition and body - nothing else
            
            IMPORTANT: This is the final output that will be executed. It must be perfect.""",
            context=final_code
        )

        return sanitized_code