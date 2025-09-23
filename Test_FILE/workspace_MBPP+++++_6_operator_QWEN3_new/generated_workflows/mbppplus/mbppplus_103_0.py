# Workflow ID: mbppplus_103_0
# Benchmark: mbppplus
# Data Indices: [341, 175]

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
        import json

        # Phase 1: Problem Classification and Intent Extraction
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Extract:
            1. Primary task category (e.g., membership testing, counting under constraints, transformation, validation)
            2. Input data types and structures (list, tuple, string, etc.)
            3. Expected output type and format
            4. Key algorithmic operations needed (iteration, comparison, aggregation, etc.)
            5. Critical edge cases (empty inputs, single elements, duplicates, boundaries)
            6. Any implied constraints or hidden requirements
            7. Recommended Pythonic approaches or built-ins that could be leveraged
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        # Generate three diverse candidate solutions in parallel
        candidate_instructions = [
            """Generate a direct, literal implementation that closely follows the reference solution's logic.
            Focus on clarity and correctness over optimization. Include all necessary imports.
            Handle all edge cases mentioned in the classification. Return exactly the expected type.""",
            
            """Generate an optimized, Pythonic implementation using built-ins, comprehensions, or set operations.
            Prioritize readability and efficiency. Include all necessary imports.
            Ensure robust edge case handling. Return exactly the expected type.""",
            
            """Generate a mathematically or algorithmically transformed solution that approaches the problem from a different angle.
            Consider functional programming, recursion, or mathematical shortcuts. Include all necessary imports.
            Handle edge cases explicitly. Return exactly the expected type."""
        ]

        candidate_tasks = [
            self.generate(
                instruction=f"""Based on this problem classification:
                {classification}

                {instr}

                IMPORTANT: Your output must be ONLY the function implementation as specified in the problem.
                No explanations, no markdown, no additional text—just the code starting with imports (if any) and the function definition.""",
                context=classification
            ) for instr in candidate_instructions
        ]

        candidates = await asyncio.gather(*candidate_tasks)

        # Phase 3: Validation and Refinement Loop
        best_candidate = None
        best_score = -1

        for iteration in range(3):  # Max 3 refinement cycles
            validation_tasks = []
            
            for i, candidate in enumerate(candidates):
                validation_tasks.append(
                    self.programmer(
                        instruction=f"""Execute this candidate solution against comprehensive test cases including edge cases.
                        Problem classification context:
                        {classification}
                        
                        Validate:
                        1. Correctness on basic and edge cases
                        2. Return type matches expected output
                        3. No runtime errors or exceptions
                        4. Handles empty inputs, single elements, duplicates appropriately
                        
                        If errors occur, provide specific error messages and line numbers.
                        If successful, output 'PASSED' followed by performance and readability assessment.""",
                        context=candidate,
                        max_retries=1
                    )
                )
            
            validations = await asyncio.gather(*validation_tasks)
            
            # Filter passed candidates and score them
            passed_candidates = []
            for i, (candidate, validation) in enumerate(zip(candidates, validations)):
                if "PASSED" in validation:
                    # Extract performance/readability score from validation
                    score = 0
                    if "efficient" in validation.lower() or "optimized" in validation.lower():
                        score += 2
                    if "readable" in validation.lower() or "clear" in validation.lower():
                        score += 1
                    if "pythonic" in validation.lower():
                        score += 1
                    passed_candidates.append((candidate, score, i))
            
            if passed_candidates:
                # Select highest scoring candidate
                passed_candidates.sort(key=lambda x: x[1], reverse=True)
                best_candidate, best_score, _ = passed_candidates[0]
                break
            else:
                # Revise candidates based on validation feedback
                revised_candidates = []
                for candidate, validation in zip(candidates, validations):
                    revised = await self.revise(
                        instruction=f"""Revise this code based on the following validation feedback:
                        {validation}
                        
                        Fix all identified errors and issues. Improve robustness for edge cases.
                        Maintain the exact function signature and return type.
                        Ensure all necessary imports are included.
                        
                        Output ONLY the revised function implementation—no explanations or additional text.""",
                        context=candidate
                    )
                    revised_candidates.append(revised)
                candidates = revised_candidates

        # Phase 4: Final Ensemble Synthesis (if multiple passed)
        if len(passed_candidates) > 1:
            synthesis_instruction = f"""Select the best solution from these candidates based on:
            1. Correctness (all must be correct)
            2. Efficiency and performance
            3. Readability and maintainability
            4. Pythonic style and idioms
            5. Edge case robustness
            
            Problem classification context:
            {classification}
            
            Return ONLY the selected function implementation—no explanations or additional text."""
            
            best_candidate = await self.ensemble(
                instruction=synthesis_instruction,
                contexts_list=[candidate for candidate, _, _ in passed_candidates]
            )

        # Final output
        if best_candidate is None and candidates:
            # Fallback: return first candidate if all else fails
            best_candidate = candidates[0]

        return best_candidate