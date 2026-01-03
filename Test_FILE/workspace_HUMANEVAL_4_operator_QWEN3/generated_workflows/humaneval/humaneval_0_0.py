# Workflow ID: humaneval_0_0
# Benchmark: humaneval
# Data Indices: [44, 72]

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
        Universal code generation workflow with parallel hypothesis generation,
        iterative critique, and synthesis.
        """
        import asyncio
        import re

        # Step 1: Generate multiple solution hypotheses in parallel
        hypothesis_instructions = [
            """Analyze the problem from a mathematical/formulaic perspective.
            - Identify underlying mathematical operations or transformations
            - Derive formulas or algorithms from the examples
            - Handle edge cases implied by examples (zero, single elements, boundaries)
            - Return code must match exact signature and types shown in examples
            - Do not over-engineer: implement only what's demonstrated or logically implied""",
            
            """Analyze the problem from an algorithmic/step-by-step perspective.
            - Break down the examples into discrete steps
            - Identify patterns in input-output transformations
            - Consider iterative, recursive, or sliding window approaches as appropriate
            - Handle edge cases: empty inputs, single elements, zeros, extremes
            - Ensure return type matches examples exactly (int vs float, string format)""",
            
            """Analyze the problem from an example-driven/test-case perspective.
            - Reverse-engineer the test cases from the examples
            - What edge cases must be handled based on example patterns?
            - What would break the solution? Test mentally against examples
            - Ensure function name matches ENTRY POINT exactly
            - Return precisely what examples show - no extra formatting or rounding""",
            
            """Analyze the problem from a constraint-based perspective.
            - Extract all explicit and implicit constraints from docstring
            - What assumptions are safe? (e.g., base < 10, positive integers only)
            - What must be validated? (input ranges, types, structures)
            - How to handle edge cases not shown but logically implied?
            - Prioritize correctness on shown examples over speculative generalization"""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # Step 2: Critique each hypothesis in parallel
        critique_instructions = [
            """Critique this solution for:
            - Correctness: Does it match all provided examples exactly?
            - Edge cases: Does it handle zeros, singles, empties, boundaries?
            - Type safety: Return types match examples precisely?
            - Function signature: Name matches ENTRY POINT exactly?
            - Over-engineering: Does it add features not demonstrated?
            - Efficiency: Is it unnecessarily complex or inefficient?
            List specific flaws and suggest precise fixes."""
        ] * len(hypotheses)

        critiques = await asyncio.gather(
            *[self.revise(instruction=instr, context=hyp) for instr, hyp in zip(critique_instructions, hypotheses)]
        )

        # Step 3: Summarize critiques to extract key issues
        summarized_critiques = await asyncio.gather(
            *[self.summarize(
                instruction="Extract only the critical flaws and essential fixes needed. Ignore minor stylistic issues.",
                context=crit
            ) for crit in critiques]
        )

        # Step 4: Revise hypotheses based on critiques
        revised_hypotheses = await asyncio.gather(
            *[self.revise(
                instruction=f"""Incorporate these critiques:
                {summary}
                
                Revise the solution to fix all identified issues while preserving correct parts.
                Ensure function name matches ENTRY POINT exactly.
                Return type must match examples precisely.
                Handle all edge cases mentioned in critiques.
                Do not add features not demonstrated in examples.""",
                context=hyp
            ) for hyp, summary in zip(hypotheses, summarized_critiques)]
        )

        # Step 5: Final ensemble synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from all revised candidates:
            - Must pass all provided examples exactly
            - Must handle all identified edge cases
            - Must have correct function name and return types
            - Choose the most elegant, efficient, and correct implementation
            - If candidates disagree on edge cases, prioritize behavior shown in examples
            - Do not over-engineer: implement only what's necessary
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=revised_hypotheses
        )

        return final_solution