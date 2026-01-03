# Workflow ID: mbppplus_123_0
# Benchmark: mbppplus
# Data Indices: [368, 224]

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

        # Phase 1: Deep Problem Analysis
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Structure your response as follows:
            1. INPUT_STRUCTURE: Describe the expected input type and format (e.g., list of tuples, list of integers, etc.)
            2. OUTPUT_STRUCTURE: Describe the required output type and format
            3. CORE_LOGIC: Explain the transformation or computation needed in plain English
            4. EDGE_CASES: List potential edge cases (empty inputs, single elements, duplicates, boundary values, etc.)
            5. COMPLEXITY_CLASS: Classify as 'TRIVIAL', 'MODERATE', or 'COMPLEX' based on:
               - TRIVIAL: Direct mapping or single operation (e.g., list indexing)
               - MODERATE: Requires iteration or simple conditionals
               - COMPLEX: Requires stateful grouping, recursion, or multi-step logic
            6. STRATEGY_SUGGESTION: Recommend initial approach (direct implementation, pseudocode planning, or decomposition)""",
            context=""
        )

        # Phase 2: Extract Complexity Classification
        complexity_match = re.search(r'COMPLEXITY_CLASS:\s*(TRIVIAL|MODERATE|COMPLEX)', analysis, re.IGNORECASE)
        complexity = complexity_match.group(1).upper() if complexity_match else "MODERATE"

        # Phase 3: Generate Synthetic Edge Cases
        edge_cases = await self.generate(
            instruction=f"""Based on the problem analysis and edge cases identified, generate 3-5 synthetic test cases that stress-test the solution.
            Include:
            - Empty input case
            - Single element case
            - Boundary value case
            - Duplicate handling case (if applicable)
            - Type consistency case
            Format each test case as: input -> expected_output (describe if output is non-obvious)""",
            context=analysis
        )

        # Phase 4: Parallel Solution Generation (Diamond Pattern)
        solution_approaches = [
            """Generate a Python solution using an imperative approach (explicit loops and conditionals).
            Focus on clarity and explicit edge case handling. Include comments for key logic steps.""",
            
            """Generate a Python solution using a functional approach (list comprehensions, map/filter, etc.).
            Prioritize conciseness while maintaining readability. Handle edge cases elegantly.""",
            
            """Generate a Python solution using built-in Python libraries or data structures (collections, itertools, etc.) if applicable.
            Optimize for efficiency and Pythonic style."""
        ]

        # Generate solutions in parallel
        solution_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context=f"Problem Analysis:\n{analysis}\n\nEdge Cases:\n{edge_cases}") 
              for instr in solution_approaches]
        )

        # Phase 5: Validation and Refinement Loop
        validated_solutions = []
        for i, candidate in enumerate(solution_candidates):
            # Validate against edge cases
            validation = await self.revise(
                instruction=f"""Critique this solution against the problem requirements and edge cases:
                - Does it handle all edge cases identified?
                - Is the output type/format correct?
                - Are there any off-by-one errors or boundary issues?
                - Is the logic robust against malformed (but type-correct) inputs?
                Suggest specific improvements if any issues are found.""",
                context=f"Solution Candidate {i+1}:\n{candidate}\n\nProblem Analysis:\n{analysis}\n\nEdge Cases:\n{edge_cases}"
            )
            
            # If validation finds issues, revise
            if "issue" in validation.lower() or "error" in validation.lower() or "fix" in validation.lower():
                revised = await self.revise(
                    instruction="Incorporate the validation feedback to fix all identified issues. Maintain the original approach style.",
                    context=f"Original Solution:\n{candidate}\n\nValidation Feedback:\n{validation}"
                )
                validated_solutions.append(revised)
            else:
                validated_solutions.append(candidate)

        # Phase 6: Ensemble Selection
        final_selection = await self.ensemble(
            instruction="""Select the best solution from the candidates based on:
            1. Correctness (handles all edge cases)
            2. Readability and clarity
            3. Efficiency and Pythonic style
            4. Robustness (defensive programming where appropriate)
            Provide ONLY the selected solution code, no explanations.""",
            contexts_list=validated_solutions
        )

        # Phase 7: Final Code Synthesis with Strict Formatting
        final_code = await self.programmer(
            instruction=f"""Generate the final Python function implementation with STRICT requirements:
            - Output ONLY the function code (no markdown, no explanations)
            - Include necessary imports INSIDE the function if needed
            - Match the EXACT function signature from the problem
            - Return the correct data type (list, tuple, set, etc.) as specified
            - Handle all edge cases identified in analysis
            - Code must be production-ready and pass rigorous testing
            
            Problem Analysis for context:
            {analysis}
            
            Selected Solution:
            {final_selection}""",
            context=final_selection
        )

        return final_code