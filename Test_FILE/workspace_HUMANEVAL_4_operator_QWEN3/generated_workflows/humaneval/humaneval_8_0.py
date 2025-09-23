# Workflow ID: humaneval_8_0
# Benchmark: humaneval
# Data Indices: [119, 93]

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

        # Step 1: Extract core components - function signature, examples, entry point
        extraction = await self.generate(
            instruction="""Extract and structure the following from the problem:
            1. Function signature (name and parameters)
            2. All examples from docstring as input-output pairs
            3. Entry point function name
            4. Key constraints (return type, edge cases mentioned)
            Format as JSON with keys: "signature", "examples", "entry_point", "constraints"
            Be meticulous - examples are the specification.""",
            context=""
        )

        # Step 2: Classify problem type and generate multiple solution strategies in parallel
        classification = await self.generate(
            instruction=f"""Analyze the extracted examples and classify the problem:
            - Pattern type: string manipulation, mathematical, algorithmic, or other
            - Key operations needed (e.g., balancing, transformation, calculation)
            - Return type consistency (string, int, bool, etc.)
            - Edge case indicators
            Based on classification, propose 3 distinct solution strategies with brief rationale.
            Use the examples as ground truth for classification.""",
            context=extraction
        )

        # Step 3: Generate candidate solutions in parallel using different strategies
        strategy_prompts = [
            f"""Generate Python code using STRATEGY 1: Direct example extrapolation.
            - Implement exactly what examples demonstrate
            - Prioritize matching example outputs over generalization
            - Include no extra features
            Context: {extraction}""",
            f"""Generate Python code using STRATEGY 2: Abstract pattern recognition.
            - Infer underlying algorithm from examples
            - Handle edge cases implied by example variety
            - Optimize for correctness across unseen inputs
            Context: {extraction}""",
            f"""Generate Python code using STRATEGY 3: Edge-case first development.
            - Start with most extreme examples
            - Build solution that handles boundaries first
            - Ensure return type matches exactly
            Context: {extraction}"""
        ]

        candidates = await asyncio.gather(
            *[self.generate(instruction=prompt, context="") for prompt in strategy_prompts]
        )

        # Step 4: Ensemble - critique and select best solution
        best_solution = await self.ensemble(
            instruction=f"""Critically evaluate all candidate solutions:
            1. Which solution most precisely matches ALL examples?
            2. Which handles edge cases best?
            3. Which has correct function name and return types?
            4. Which is simplest without being incomplete?
            Select the single best solution. If none are perfect, synthesize a hybrid.
            Return ONLY the Python code, nothing else.
            Reference examples: {extraction}""",
            contexts_list=candidates
        )

        # Step 5: Iterative refinement - simulate test cases and fix gaps
        refined = best_solution
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Simulate test case validation:
                - Check if function name matches entry point exactly
                - Verify return types match examples precisely
                - Identify any edge cases from examples that might fail
                - Look for off-by-one errors, type mismatches, or logic gaps
                If no issues found, return 'VALID'. Otherwise, describe fixes needed.
                Current code: {refined}
                Examples: {extraction}""",
                context=refined
            )
            
            if "VALID" in validation.upper():
                break
                
            refined = await self.revise(
                instruction=f"""Fix the identified issues while preserving core logic:
                Issues to fix: {validation}
                Constraints: Must match examples exactly, correct function name, no over-engineering.
                Return ONLY the corrected Python code.""",
                context=refined
            )

        # Step 6: Final sanity check - ensure strict compliance
        final_code = await self.revise(
            instruction="""Final compliance check:
            - Function name must match ENTRY POINT exactly
            - Return types must match examples precisely (int vs float, string case, etc.)
            - No extra imports or unused variables
            - Code must be minimal - implement only what's specified
            If any compliance issues, fix them. Return ONLY the Python code.""",
            context=refined
        )

        return final_code