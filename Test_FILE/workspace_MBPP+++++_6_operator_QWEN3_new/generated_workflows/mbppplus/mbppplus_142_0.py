# Workflow ID: mbppplus_142_0
# Benchmark: mbppplus
# Data Indices: [93, 214]

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

        # PHASE 1: Problem Decomposition - Extract structural DNA
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its core components:
            1. Identify input types and structures (list, dict, string, etc.)
            2. Identify expected output type and format
            3. Determine if mutation is allowed or if new structure should be returned
            4. List potential edge cases (empty inputs, single elements, duplicates, boundaries)
            5. Suggest 2-3 algorithmic approaches that could solve this (e.g., two-pointer, set operations, sorting, etc.)
            6. Note any constraints on time/space complexity if implied
            Format each component clearly with labels.""",
            context=""
        )

        # Convert decomposition list to string for context passing
        decomposition_text = "\n".join([f"{item['id']}: {item['description']}" for item in decomposition])

        # PHASE 2: Parallel Hypothesis Generation
        hypothesis_instructions = [
            """Write a solution focusing on functional purity: no mutation, create new data structures. 
            Prioritize readability and explicit edge case handling. Use comprehensions and built-ins where appropriate.""",
            
            """Write a solution focusing on in-place efficiency and minimal memory usage. 
            Use index manipulation and avoid creating unnecessary intermediate structures. 
            Include detailed comments explaining the mutation strategy.""",
            
            """Write a solution using set-theoretic or mathematical operations. 
            Leverage Python's built-in set, sorted, or itertools operations. 
            Ensure type conversions are explicit and match expected return types.""",
            
            """Write a solution using imperative loops and conditionals. 
            Make control flow explicit and easy to trace. 
            Include defensive checks for all edge cases identified in decomposition."""
        ]

        hypotheses = await asyncio.gather(*[
            self.generate(
                instruction=f"""Based on this problem decomposition:
                {decomposition_text}

                {hyp_instruction}

                IMPORTANT: 
                - Use the exact function signature from the problem
                - Include all necessary imports inside the function if needed
                - Return the exact data type specified (list vs tuple vs set)
                - Handle all edge cases mentioned in decomposition
                - Write ONLY the function implementation, nothing else""",
                context=decomposition_text
            ) for hyp_instruction in hypothesis_instructions
        ])

        # PHASE 3: Validation and Revision Loop
        revised_hypotheses = []
        for hypothesis in hypotheses:
            try:
                # Validate with programmer (max_retries=1 to catch obvious errors)
                validation = await self.programmer(
                    instruction="Validate this code for syntax, basic logic, and type consistency. Run minimal test cases if possible.",
                    context=hypothesis,
                    max_retries=1
                )
                
                # Revise based on validation feedback
                revised = await self.revise(
                    instruction=f"""Improve this code based on validation feedback and domain requirements:
                    - Fix any syntax or type errors revealed in validation
                    - Ensure return type EXACTLY matches problem requirements
                    - Add explicit handling for edge cases: empty inputs, single elements, duplicates
                    - Preserve order if required by problem
                    - Do NOT change function signature
                    - Return ONLY the function implementation, no explanations
                    
                    Validation feedback: {validation}""",
                    context=hypothesis
                )
                revised_hypotheses.append(revised)
            except Exception as e:
                # If validation fails catastrophically, keep original but flag for ensemble
                revised_hypotheses.append(f"# VALIDATION_FAILED: {str(e)}\n{hypothesis}")

        # PHASE 4: Synthesis and Selection via Ensemble
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            1. Compare edge case handling - select the most robust
            2. Compare type correctness - ensure return type matches exactly
            3. Compare algorithmic efficiency and clarity
            4. Merge strengths: take defensive checks from one, efficiency from another
            5. Ensure function signature is preserved exactly
            6. Remove any validation failure comments or flags
            7. Return ONLY the final function implementation, nothing else
            
            If all candidates have flaws, create a new synthesis that combines their strongest elements.
            Prioritize correctness and edge case handling over elegance or brevity.""",
            contexts_list=revised_hypotheses
        )

        # PHASE 5: Stealth Edge Case Injection (Defensive Over-Engineering)
        edge_enhanced = await self.generate(
            instruction=f"""Enhance this solution with explicit handling of 5 additional edge cases not shown in examples:
            1. Empty input (empty dict, empty list, etc.)
            2. Single element input
            3. All duplicate elements
            4. Boundary values (max/min integers, empty strings, etc.)
            5. Unexpected but plausible input (None values, mixed types if applicable)
            
            For each edge case:
            - Add a comment explaining the case
            - Implement explicit handling
            - Ensure return type remains consistent
            
            Return ONLY the enhanced function implementation, nothing else.
            
            Current solution: {final_solution}""",
            context=final_solution
        )

        # PHASE 6: Final Validation and Cleanup
        # One last revision to ensure cleanliness and specification compliance
        final_output = await self.revise(
            instruction="""Final cleanup and specification compliance check:
            - Remove any debug prints or unnecessary comments
            - Ensure ONLY the function implementation is returned (no markdown, no explanations)
            - Verify function signature matches exactly (parameter names, order)
            - Verify return type is correct (list vs tuple vs set)
            - Ensure no external dependencies beyond standard library
            - If any uncertainty remains, prioritize robustness and specification compliance
            
            Return ONLY the clean function implementation.""",
            context=edge_enhanced
        )

        return final_output