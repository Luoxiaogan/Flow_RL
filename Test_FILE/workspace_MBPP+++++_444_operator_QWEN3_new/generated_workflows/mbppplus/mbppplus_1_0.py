# Workflow ID: mbppplus_1_0
# Benchmark: mbppplus
# Data Indices: [341, 61, 138]

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
        import math  # Pre-import common modules; revise will add others if needed

        # Phase 1: Problem Decomposition & Typing
        problem_analysis = await self.generate(
            instruction="""Perform deep problem decomposition:
            1. Identify the core operation: What is the function supposed to compute/transform?
            2. Classify problem type: Is it numerical, logical, transformational, or hybrid?
            3. Extract implicit constraints: Return type? Order preservation? Mutability? Edge cases?
            4. Identify required imports: Does it need math, itertools, etc.?
            5. Note any ambiguities that need resolution.
            Output as structured bullet points.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        literal_solution_task = self.generate(
            instruction=f"""Generate a solution that follows the problem description literally:
            - Prioritize direct interpretation over elegance
            - Handle obvious edge cases (empty inputs, single elements)
            - Match expected return type exactly
            - Use minimal abstraction
            Problem context: {problem_analysis}""",
            context=""
        )

        robust_solution_task = self.generate(
            instruction=f"""Generate a solution focused on robustness:
            - Actively consider edge cases: empty, max/min, duplicates, type mismatches
            - Include defensive checks if needed
            - Prefer built-ins and standard library for reliability
            - Document assumptions made
            Problem context: {problem_analysis}""",
            context=""
        )

        elegant_solution_task = self.generate(
            instruction=f"""Generate the most elegant/mathematically sound solution:
            - Prioritize clarity and efficiency
            - Use advanced Python features if appropriate (comprehensions, any(), etc.)
            - Minimize lines of code without sacrificing readability
            - Consider algorithmic complexity
            Problem context: {problem_analysis}""",
            context=""
        )

        literal_solution, robust_solution, elegant_solution = await asyncio.gather(
            literal_solution_task, robust_solution_task, elegant_solution_task
        )

        # Phase 3: Parallel Edge-Case Validation
        def create_validator(solution, label):
            return self.revise(
                instruction=f"""Stress-test this solution by generating and testing against edge cases:
                - Empty inputs
                - Single-element inputs
                - Boundary values (0, -1, maxint, etc.)
                - Type mismatches (if applicable)
                - Duplicates (if applicable)
                - Performance stress (large inputs if relevant)
                Report any failures or weaknesses. If none, confirm robustness.
                Solution to validate: {label}
                --- SOLUTION ---
                {solution}""",
                context=solution
            )

        validations = await asyncio.gather(
            create_validator(literal_solution, "Literal"),
            create_validator(robust_solution, "Robust"),
            create_validator(elegant_solution, "Elegant")
        )

        # Phase 4: Ensemble Synthesis with Constraint Reconciliation
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these three candidates:
            CRITERIA (in order of priority):
            1. Correctness under all edge cases (refer to validation reports)
            2. Adherence to implicit constraints (return type, order, mutability)
            3. Code clarity and maintainability
            4. Efficiency and elegance
            
            INTEGRATE improvements:
            - Adopt defensive checks from Robust version if missing
            - Prefer elegant constructs from Elegant version if correct
            - Ensure literal interpretation matches problem intent
            
            OUTPUT ONLY THE FINAL FUNCTION IMPLEMENTATION:
            - Include necessary imports at top
            - Exact function signature as in problem
            - No markdown, no explanations, no comments
            - Return appropriate data types
            
            Validation reports:
            Literal: {validations[0]}
            Robust: {validations[1]}
            Elegant: {validations[2]}
            """,
            contexts_list=[literal_solution, robust_solution, elegant_solution]
        )

        # Phase 5: Final Refinement (ensure code-only output, correct imports)
        clean_code = await self.revise(
            instruction="""Final cleanup:
            1. Remove any explanatory text, comments, or markdown
            2. Ensure ONLY the function implementation is present
            3. Verify imports are included if used (math, etc.)
            4. Match function signature exactly
            5. Return appropriate data types (list vs tuple vs set)
            6. Strip any trailing whitespace or extra newlines
            Output ONLY the raw Python code block.""",
            context=final_solution
        )

        return clean_code