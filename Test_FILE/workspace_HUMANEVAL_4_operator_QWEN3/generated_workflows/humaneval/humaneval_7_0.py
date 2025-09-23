# Workflow ID: humaneval_7_0
# Benchmark: humaneval
# Data Indices: [156, 142]

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
        Universal workflow for generating Python functions from docstring specifications.
        Dynamically classifies problem, explores multiple solution strategies in parallel,
        critiques them, and synthesizes a robust final solution.
        """
        import asyncio

        # Phase 1: Problem Classification & Specification Mining
        specification_analysis = await self.generate(
            instruction="""You are a senior software architect. Analyze the given function specification and examples to produce a structured problem breakdown. Include:

1. Problem Type Classification: Is this primarily mathematical, string manipulation, list processing, algorithmic, or logical?
2. Input/Output Specification: What are the exact types and constraints of inputs and outputs?
3. Pattern Extraction: What transformation rules can be inferred from the examples? Show input → output mappings and deduce the underlying logic.
4. Edge Case Identification: What boundary conditions, special cases, or potential pitfalls are implied but not explicitly shown in the examples?
5. Return Type Precision: Must the return type match exactly (e.g., int vs float, str case sensitivity)?

Format your response as a clear, structured analysis with headings for each section. Do not write code yet.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        # Spawn three different solution strategies based on the problem analysis
        strategy_tasks = [
            self.generate(
                instruction=f"""You are an expert Python developer. Implement the function using a MATHEMATICAL/FORMULA-BASED approach.
Context: {specification_analysis}

Guidelines:
- Focus on deriving formulas, mathematical decompositions, or algebraic transformations.
- Use minimal state and loops; prefer direct computation.
- Ensure return type matches specification exactly.
- Handle edge cases identified in the analysis.
- Function name must match ENTRY POINT exactly.

Write ONLY the function implementation, no explanations.""",
                context=specification_analysis
            ),
            self.generate(
                instruction=f"""You are an expert Python developer. Implement the function using an IMPERATIVE/STEP-BY-STEP approach.
Context: {specification_analysis}

Guidelines:
- Use explicit loops, conditionals, and state variables.
- Break down the problem into clear sequential steps.
- Ensure return type matches specification exactly.
- Handle edge cases identified in the analysis.
- Function name must match ENTRY POINT exactly.

Write ONLY the function implementation, no explanations.""",
                context=specification_analysis
            ),
            self.generate(
                instruction=f"""You are an expert Python developer. Implement the function by DIRECTLY EXTRAPOLATING from the provided examples.
Context: {specification_analysis}

Guidelines:
- Study the input-output examples and derive transformation rules.
- Implement the most direct mapping from examples to code.
- Ensure return type matches specification exactly.
- Handle edge cases identified in the analysis.
- Function name must match ENTRY POINT exactly.

Write ONLY the function implementation, no explanations.""",
                context=specification_analysis
            )
        ]

        # Execute strategies in parallel
        candidate_solutions = await asyncio.gather(*strategy_tasks)

        # Phase 3: Parallel Critique of Each Candidate
        critique_tasks = [
            self.revise(
                instruction=f"""You are a meticulous code reviewer. Critique this candidate solution against the original problem specification and examples. Do NOT fix it — only analyze.

Checklist:
1. Does it handle ALL examples correctly?
2. Are edge cases (identified in specification analysis) properly handled?
3. Is the return type exactly as specified?
4. Does the function name match ENTRY POINT exactly?
5. Are there any logical flaws, off-by-one errors, or unhandled conditions?

Provide a concise bullet-point critique. If no issues, state 'No issues found.'""",
                context=candidate
            ) for candidate in candidate_solutions
        ]

        critiques = await asyncio.gather(*critique_tasks)

        # Phase 4: Ensemble Synthesis with Meta-Validation
        final_solution = await self.ensemble(
            instruction=f"""You are the lead architect synthesizing the final solution. You have three candidate implementations and their critiques.

Your task:
1. Analyze each candidate and its critique.
2. Synthesize the best elements into a single, robust implementation.
3. Ensure ALL edge cases are handled.
4. Match return type and function name EXACTLY as specified.
5. Prefer clarity and correctness over cleverness.
6. If conflicts exist between candidates, choose the most logically sound approach.

Output ONLY the final function implementation, no explanations or markdown.""",
            contexts_list=[
                f"Candidate 1:\n{candidate_solutions[0]}\nCritique:\n{critiques[0]}",
                f"Candidate 2:\n{candidate_solutions[1]}\nCritique:\n{critiques[1]}",
                f"Candidate 3:\n{candidate_solutions[2]}\nCritique:\n{critiques[2]}"
            ]
        )

        # Phase 5: Optional Validation Simulation (Single Iteration)
        validation_check = await self.generate(
            instruction=f"""You are writing unit tests based ONLY on the examples in the docstring. Given this implementation:

{final_solution}

And the original examples, does this code pass all specified test cases? Identify any mismatches. If it passes, respond with 'PASSES'. If not, list failing cases and why.""",
            context=final_solution
        )

        # If validation fails, attempt one revision
        if "PASSES" not in validation_check.upper():
            final_solution = await self.revise(
                instruction=f"""Revise this implementation to fix the issues identified in validation:

Validation Feedback:
{validation_check}

Ensure:
- All examples are handled correctly.
- Edge cases are covered.
- Return type and function name are exact.
- No over-engineering — implement exactly what's specified.

Output ONLY the corrected function.""",
                context=final_solution
            )

        return final_solution