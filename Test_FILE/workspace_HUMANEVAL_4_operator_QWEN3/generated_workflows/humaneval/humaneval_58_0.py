# Workflow ID: humaneval_58_0
# Benchmark: humaneval
# Data Indices: [61, 153]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for generating Python functions from specifications.
        Dynamically adapts strategy based on problem type, validates against examples,
        and refines through simulated execution.
        """
        import asyncio
        import re

        # Step 1: Classify the problem type and extract key constraints
        classification = await self.generate(
            instruction="""Analyze the problem specification and classify it into one of the following categories:
            - 'stateful_string_traversal': Problems involving strings where state (e.g., counter, stack) must be maintained and validated (e.g., bracket matching).
            - 'scoring_and_selection': Problems requiring computation of scores for items in a collection and selecting the best (e.g., strongest extension).
            - 'mathematical_formula': Problems solvable by deriving a direct mathematical expression or formula.
            - 'recursive_or_iterative_pattern': Problems requiring recursion or iterative pattern recognition.
            - 'filtering_or_mapping': Problems involving transforming or filtering lists/strings based on conditions.
            
            Additionally, extract:
            - Whether early termination is possible (e.g., invalid state detected midway).
            - Whether tie-breaking rules exist (e.g., first occurrence wins).
            - Whether return type must be exact (int vs float, bool, etc.).
            - Any implicit edge cases hinted in examples (empty input, single element, etc.).
            
            Format your response as a structured JSON-like block with keys: 'category', 'constraints', 'edge_hints'.""",
            context=""
        )

        # Step 2: Generate two solution candidates in parallel — one strategy-driven, one naive
        strategy_solution_task = self.generate(
            instruction=f"""Generate a Python function implementation based on the problem classification:
            Classification: {classification}
            
            Guidelines:
            - If 'stateful_string_traversal', use a counter or stack; return early if state becomes invalid.
            - If 'scoring_and_selection', iterate and compute score per item; track maximum with tie-breaking.
            - If 'mathematical_formula', derive and implement the formula directly.
            - Ensure function name matches ENTRY POINT exactly.
            - Return type must match examples precisely (e.g., int, float, bool).
            - Do not add imports unless absolutely necessary (they will be auto-added).
            - Handle edge cases mentioned in classification.
            
            Output ONLY the function code, nothing else.""",
            context=classification
        )

        naive_solution_task = self.generate(
            instruction="""Generate a Python function by directly translating the examples in the docstring into code.
            Do not overthink — mimic the pattern shown in examples as literally as possible.
            - Use the exact function name from ENTRY POINT.
            - Match return types exactly as shown in examples.
            - Do not add comments or explanations.
            - Output ONLY the function code.""",
            context=""
        )

        # Execute both in parallel
        strategy_solution, naive_solution = await asyncio.gather(strategy_solution_task, naive_solution_task)

        # Step 3: Ensemble to select the best candidate
        selected_solution = await self.ensemble(
            instruction="""Compare the two solution candidates and select the best one based on:
            1. Faithfulness to the problem specification and examples.
            2. Handling of edge cases (especially those hinted in classification).
            3. Structural soundness (e.g., early termination where appropriate, correct tie-breaking).
            4. Simplicity and directness — avoid over-engineering.
            
            If both are equally valid, prefer the strategy-driven solution.
            Output ONLY the selected function code, nothing else.""",
            contexts_list=[strategy_solution, naive_solution]
        )

        # Step 4: Revise by simulating execution against examples
        refined_solution = selected_solution
        for _ in range(2):  # Allow up to 2 refinement iterations
            validation_feedback = await self.generate(
                instruction=f"""Simulate the execution of the following code against EACH example in the docstring:
                Code:
                {refined_solution}
                
                For each example:
                - Write out step-by-step variable states.
                - Verify the final output matches the expected result.
                - If any mismatch, explain exactly why and propose a fix.
                - Also check: function name matches ENTRY POINT, return type is exact, no extra imports.
                
                If no issues, respond with 'VALID'.
                Otherwise, respond with a detailed fix description.""",
                context=refined_solution
            )

            if "VALID" in validation_feedback.upper():
                break

            # Revise based on feedback
            refined_solution = await self.revise(
                instruction=f"""Fix the code based on this feedback:
                {validation_feedback}
                
                Ensure:
                - Function name is unchanged and matches ENTRY POINT.
                - Return types are preserved exactly.
                - Edge cases from classification are handled.
                - Code remains minimal — no over-engineering.
                
                Output ONLY the corrected function code.""",
                context=refined_solution
            )

        # Step 5: Final compliance check (function signature, return type, no extra imports)
        final_code = await self.summarize(
            instruction=f"""Verify strict compliance:
            - Function name must exactly match the ENTRY POINT specified in the problem.
            - Return type must match all examples (e.g., if examples return int, never return float).
            - No extra imports or helper functions unless absolutely necessary (imports will be auto-added).
            - Code must be self-contained and match the specification exactly.
            
            If compliant, output the code unchanged.
            If not, make minimal edits to ensure compliance.
            
            Output ONLY the final function code.""",
            context=refined_solution
        )

        return final_code