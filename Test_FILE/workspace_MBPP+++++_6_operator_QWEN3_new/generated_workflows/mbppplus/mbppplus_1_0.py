# Workflow ID: mbppplus_1_0
# Benchmark: mbppplus
# Data Indices: [330, 263]

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

        # Phase 1: Problem Classification & Strategy Inference
        classification = await self.generate(
            instruction="""Analyze this programming problem deeply and classify it along multiple dimensions:
            1. Problem Type: Is it mathematical (closed-form formula), structural (string/list manipulation), logical (condition/filter), or hybrid?
            2. Solution Strategy: Does it require direct computation, iteration, recursion, filtering, or transformation?
            3. Data Structures: What input/output types are involved (lists, tuples, strings, numbers)? Must order be preserved?
            4. Edge Cases: What are the critical edge cases (empty inputs, single elements, zeros, negatives, duplicates)?
            5. Complexity: Is an efficient algorithm required, or is brute force acceptable?
            6. Validation: What sample cases are provided, and what do they imply about expected behavior?
            
            Output your analysis in a structured format with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Assuming this is a MATHEMATICAL problem, generate a solution:
                - Derive or recall the mathematical formula
                - Handle edge cases: 0, 1, negative numbers
                - Ensure return type matches sample outputs
                - Show step-by-step reasoning
                Problem context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Assuming this is a STRUCTURAL/LIST problem, generate a solution:
                - Identify the transformation/filter pattern
                - Preserve order if required
                - Handle empty lists and single elements
                - Use appropriate data structures (list vs tuple vs set)
                - Show step-by-step reasoning
                Problem context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Assuming this is a STRING/LOGICAL problem, generate a solution:
                - Define the logical condition or pattern
                - Handle edge cases: empty strings, single characters
                - Consider case sensitivity, whitespace, encoding
                - Show step-by-step reasoning
                Problem context: {classification}""",
                context=""
            )
        )

        # Phase 3: Strategy Selection via Ensemble
        selected_strategy = await self.ensemble(
            instruction="""Evaluate the three solution strategies and select the most appropriate one:
            1. Which strategy best matches the problem classification?
            2. Which solution handles all identified edge cases?
            3. Which approach is most aligned with the sample test cases?
            4. Which solution is most efficient and readable?
            5. If multiple are valid, synthesize the best elements into one coherent approach.
            
            Output the selected (or synthesized) solution strategy with clear justification.""",
            contexts_list=strategy_attempts
        )

        # Phase 4: Code Generation with Edge Case Enforcement
        initial_code = await self.programmer(
            instruction=f"""Generate Python code that implements the selected strategy:
            - Use the exact function signature from the problem
            - Include all necessary imports
            - Handle ALL edge cases identified in classification
            - Match return types exactly (list vs tuple vs int vs float)
            - Include brief comments explaining key steps
            - Code must be production-ready and pass rigorous testing
            Selected strategy: {selected_strategy}""",
            context=classification
        )

        # Phase 5: Validation & Self-Testing
        validation = await self.generate(
            instruction=f"""Critically validate the generated code:
            1. Execute the sample test cases mentally: do outputs match?
            2. Test edge cases: empty inputs, single elements, boundary values
            3. Check type consistency: does return type match expectations?
            4. Verify efficiency: is there unnecessary complexity?
            5. Identify any potential bugs or oversights
            
            If any issues are found, describe them specifically. If perfect, say 'VALIDATED'.
            Code to validate: {initial_code}""",
            context=selected_strategy
        )

        # Phase 6: Conditional Revision Loop
        current_code = initial_code
        for _ in range(3):  # Max 3 revision attempts
            if "VALIDATED" in validation and "bug" not in validation.lower() and "error" not in validation.lower():
                break
                
            current_code = await self.revise(
                instruction=f"""Fix the identified issues in the code:
                - Address all validation concerns specifically
                - Preserve correct functionality while fixing bugs
                - Maintain clean, readable code structure
                - Re-check edge cases after revision
                Validation feedback: {validation}""",
                context=current_code
            )
            
            # Re-validate
            validation = await self.generate(
                instruction=f"""Re-validate the revised code against same criteria:
                1. Sample cases
                2. Edge cases
                3. Type consistency
                4. Efficiency
                5. Bug detection
                Revised code: {current_code}""",
                context=validation
            )

        # Phase 7: Final Output Generation
        final_code = await self.generate(
            instruction=f"""Extract ONLY the Python function code from the solution:
            - Remove any markdown, explanations, or extra text
            - Keep all imports inside the function if needed
            - Preserve exact function signature
            - Ensure code is ready for automated testing
            - Return pure code block without any additional text
            Final validated solution: {current_code}""",
            context=current_code
        )

        # Clean extraction (remove markdown code fences if present)
        code_lines = []
        in_code_block = False
        for line in final_code.split('\n'):
            if line.strip().startswith('