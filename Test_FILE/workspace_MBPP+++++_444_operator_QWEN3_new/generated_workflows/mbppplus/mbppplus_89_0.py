# Workflow ID: mbppplus_89_0
# Benchmark: mbppplus
# Data Indices: [142, 125, 80]

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

        # PHASE 1: Deep Problem Classification
        classification = await self.generate(
            instruction="""Perform comprehensive problem analysis. Extract and structure:
            1. Function signature and expected input/output types
            2. Core operation type (mathematical, structural, logical, transformation)
            3. Key algorithmic patterns (iteration, recursion, slicing, factorization, etc.)
            4. Critical edge cases (empty inputs, single elements, zeros, negatives, boundaries)
            5. Expected failure modes and common pitfalls
            6. Reference solution approach if discernible
            Format as structured JSON-like text with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (Diamond Pattern)
        naive_solution, robust_solution, textbook_solution = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a NAIVE but clear solution based on:
                Classification: {classification}
                
                Requirements:
                - Prioritize readability and direct implementation
                - Use straightforward logic even if inefficient
                - Include comments explaining each step
                - Do NOT optimize prematurely""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a ROBUST, edge-case-aware solution based on:
                Classification: {classification}
                
                Requirements:
                - Handle ALL identified edge cases explicitly
                - Include input validation and defensive programming
                - Optimize for correctness over performance
                - Add assertions or inline checks where appropriate""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a TEXTBOOK/OPTIMIZED solution based on:
                Classification: {classification}
                
                Requirements:
                - Mimic reference solution patterns if detectable
                - Prioritize efficiency and elegance
                - Use idiomatic Python and built-in functions
                - Assume inputs are well-formed (focus on core logic)""",
                context=classification
            )
        )

        # PHASE 3: Ensemble Synthesis
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a FINAL SOLUTION by combining the best elements from all three approaches:
            - Take clarity and structure from the NAIVE solution
            - Incorporate edge-case handling from the ROBUST solution
            - Adopt efficiency and elegance from the TEXTBOOK solution
            
            Output ONLY the final function implementation with:
            - Exact function signature as in original problem
            - All necessary imports inside the function if needed
            - No wrapper code, classes, or extra text
            - Clean, production-ready code""",
            contexts_list=[naive_solution, robust_solution, textbook_solution]
        )

        # PHASE 4: Iterative Validation & Refinement
        current_solution = synthesized_solution
        for iteration in range(3):  # Max 3 refinement cycles
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this solution against problem requirements:
                Original Classification: {classification}
                Current Solution: {current_solution}
                
                Check for:
                - Correct function signature and return type
                - Handling of all edge cases identified in classification
                - Logical correctness and algorithmic soundness
                - Adherence to Python best practices
                - No extraneous output or debugging code
                
                If issues found, provide specific, actionable revision instructions.
                If perfect, respond with 'VALIDATED'.""",
                context=current_solution
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise the solution based on this feedback:
                {validation_feedback}
                
                Preserve:
                - Core logic and algorithmic approach
                - Readability and structure
                - Edge case handling
                
                Fix:
                - Type mismatches
                - Logical errors
                - Missing edge cases
                - Style violations
                
                Output ONLY the revised function implementation.""",
                context=current_solution
            )

        # PHASE 5: Final Cleanup & Format Compliance
        final_implementation = await self.summarize(
            instruction="""Extract ONLY the final function implementation with strict format compliance:
            - Remove all comments, explanations, and markdown
            - Ensure exact function signature matches original problem
            - Include imports inside function if needed
            - Return pure Python code ready for execution
            - No extra text, wrappers, or formatting""",
            context=current_solution
        )

        return final_implementation