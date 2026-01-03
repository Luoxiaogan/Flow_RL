# Workflow ID: mbppplus_97_0
# Benchmark: mbppplus
# Data Indices: [13, 232, 322]

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

        # PHASE 1: Problem Classification and Edge Case Identification
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Classify the algorithmic category: Is this a reduction, traversal, recursion, transformation, or combinatorial problem?
            2. Identify input data structures: lists, tuples, dicts, strings, primitives?
            3. Identify output requirements: scalar, list, tuple, boolean?
            4. Extract all edge conditions: empty inputs, single elements, boundary values, type edge cases.
            5. Infer time/space complexity constraints from problem context.
            6. Predict common failure modes for naive implementations.
            Format as structured JSON with keys: category, inputs, outputs, edge_cases, complexity, failure_modes.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using IMPERATIVE style:
                - Use explicit loops and conditionals
                - Handle all edge cases identified in classification: {classification}
                - Include detailed comments explaining logic
                - Match exact function signature and return type
                - Prioritize readability over brevity""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution using FUNCTIONAL style:
                - Use map/filter/reduce or comprehensions
                - Avoid explicit loops where possible
                - Handle edge cases from classification: {classification}
                - Include type-aware operations
                - Match exact signature and return type""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate a solution using RECURSIVE style (if applicable):
                - Define clear base cases aligned with edge cases: {classification}
                - Ensure proper state transitions
                - Include termination guarantees
                - Match signature and return type
                - Add recursion depth comments if relevant""",
                context=classification
            )
        )

        # PHASE 3: Strategy Synthesis
        synthesized = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions:
            1. Select the most appropriate paradigm based on problem classification
            2. Combine robust edge case handling from all versions
            3. Preserve type consistency and signature compliance
            4. Optimize for clarity and correctness over cleverness
            5. Return ONLY the final function implementation with imports if needed
            6. Do NOT include explanations or markdown - pure executable code""",
            contexts_list=strategies
        )

        # PHASE 4: Iterative Validation and Refinement
        current_solution = synthesized
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Rigorous validation of current solution:
                1. Execute against all provided test cases mentally
                2. Identify specific line numbers or logic blocks that may fail
                3. Check type consistency: input types, output types, intermediate types
                4. Verify edge case coverage from classification: {classification}
                5. If no issues found, return 'VALIDATED'
                6. If issues found, describe exact failure and required fix
                Be brutally honest - correctness is paramount.""",
                context=current_solution
            )
            
            if "VALIDATED" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise solution based on validation feedback:
                Validation issues: {validation}
                Original classification: {classification}
                Requirements:
                - Fix ONLY the identified issues
                - Preserve working parts of solution
                - Maintain exact function signature
                - Do NOT change approach unless absolutely necessary
                - Return complete corrected implementation""",
                context=current_solution
            )

        # FINAL OUTPUT EXTRACTION
        # Extract just the code block if wrapped in markdown
        code_match = re.search(r'