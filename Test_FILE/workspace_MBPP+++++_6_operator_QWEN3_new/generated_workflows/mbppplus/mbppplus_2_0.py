# Workflow ID: mbppplus_2_0
# Benchmark: mbppplus
# Data Indices: [289, 156]

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

        # PHASE 1: Problem Classification & Strategy Selection
        classification = await self.generate(
            instruction="""Thoroughly classify this programming problem by analyzing its structure, inputs, outputs, and implied operations. Your classification must include:
            1. Problem Category: Is it mathematical, string manipulation, list/set operation, logic/validation, or data structure algorithm?
            2. Key Operations: What core Python operations or algorithms are likely needed (e.g., set difference, string reversal, index comparison, sorting)?
            3. Edge Cases: What edge cases must be handled (empty inputs, single elements, duplicates, type boundaries)?
            4. Solution Strategy: Recommend 2-3 distinct implementation approaches (e.g., brute force, optimized, functional, set-based, index-based).
            5. Output Requirements: Infer expected return type and function signature constraints.
            Format your response as a structured markdown list with clear headings.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (Diamond Pattern)
        # Generate 3 candidate solutions using different strategies
        solution_tasks = [
            self.programmer(
                instruction=f"""Implement a solution using a BRUTE FORCE / STRAIGHTFORWARD approach.
                Classification context: {classification}
                Requirements:
                - Prioritize correctness and readability over optimization.
                - Handle all edge cases mentioned in classification.
                - Use exact function name and parameters from problem.
                - Return correct data type as inferred.
                - Include necessary imports inside function if needed.
                Generate ONLY the function implementation, no explanations.""",
                context=classification
            ),
            self.programmer(
                instruction=f"""Implement a solution using an OPTIMIZED / PYTHONIC approach.
                Classification context: {classification}
                Requirements:
                - Use built-in functions, comprehensions, or efficient algorithms.
                - Handle edge cases explicitly.
                - Match exact function signature.
                - Ensure return type consistency.
                - Include imports inside function.
                Generate ONLY the function implementation, no explanations.""",
                context=classification
            ),
            self.programmer(
                instruction=f"""Implement a solution focused on EDGE CASE ROBUSTNESS.
                Classification context: {classification}
                Requirements:
                - Explicitly check for and handle all edge cases from classification.
                - Use defensive programming patterns.
                - Maintain function signature exactly.
                - Validate input types and lengths where appropriate.
                - Include necessary imports.
                Generate ONLY the function implementation, no explanations.""",
                context=classification
            )
        ]
        
        candidate_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 3: Validation & Refinement Loop (Iterative Feedback)
        refined_solutions = []
        for i, solution in enumerate(candidate_solutions):
            current_solution = solution
            for revision_round in range(2):  # Max 2 revisions
                validation_feedback = await self.generate(
                    instruction=f"""Critically validate this solution against the problem requirements and edge cases:
                    Solution: {current_solution}
                    Classification: {classification}
                    Check for:
                    1. Correct function name and parameter order.
                    2. Proper handling of edge cases (empty, single element, duplicates, boundaries).
                    3. Correct return type and structure.
                    4. No unnecessary imports or wrapper code.
                    5. Logical correctness for sample cases.
                    If any issues found, describe them specifically. If perfect, say 'VALID'.""",
                    context=current_solution
                )
                
                if "VALID" in validation_feedback.upper() and "ISSUE" not in validation_feedback.upper():
                    break  # No issues found, exit revision loop
                
                # Revise based on feedback
                current_solution = await self.revise(
                    instruction=f"""Revise this solution to fix the issues identified in feedback:
                    Feedback: {validation_feedback}
                    Requirements:
                    - Fix all identified issues while preserving core logic.
                    - Maintain exact function signature.
                    - Keep code clean and readable.
                    - Include necessary imports inside function.
                    Return ONLY the revised function implementation.""",
                    context=current_solution
                )
            
            refined_solutions.append(current_solution)

        # PHASE 4: Ensemble Selection (Synthesis & Decision)
        final_solution = await self.ensemble(
            instruction="""Select the BEST solution from the candidates below based on:
            1. Correctness: Handles all edge cases and matches expected behavior.
            2. Signature Compliance: Exact function name, parameters, and return type.
            3. Code Quality: Readable, efficient, and clean implementation.
            4. Robustness: Explicit edge case handling and defensive patterns.
            If multiple solutions are valid, prefer the most efficient or simplest.
            You may also SYNTHESIZE a new solution by combining the best parts of multiple candidates.
            Return ONLY the final function implementation, no explanations or markdown.""",
            contexts_list=refined_solutions
        )

        # PHASE 5: Final Compliance Check
        compliant_solution = await self.revise(
            instruction="""Perform final compliance check:
            1. Ensure function name EXACTLY matches problem specification.
            2. Parameter names and order must be identical.
            3. Return type must match test case expectations.
            4. All imports must be inside the function if needed.
            5. NO wrapper code, explanations, or markdown formatting.
            6. Code must be ready for direct execution.
            If any compliance issues, fix them immediately.
            Return ONLY the cleaned, compliant function implementation.""",
            context=final_solution
        )

        return compliant_solution