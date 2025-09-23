# Workflow ID: mgsmbn_2_0
# Benchmark: mgsmbn
# Data Indices: [125]

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

        # PHASE 1: Problem Decomposition & Entity Extraction
        decomposition = await self.decompose(
            instruction="""Break this Bengali math problem into atomic, solvable subproblems.
            For each subproblem:
            - Identify the mathematical operation required (add, subtract, multiply, divide, convert, etc.)
            - Extract all numerical values and their associated units/entities
            - Specify dependencies (which subproblems must be solved first)
            - Flag any culturally specific terms or ambiguous phrasing
            - Mandate unit normalization (convert all to target unit before calculation)
            Return structured subproblems with clear IDs and dependency chains.""",
            context=""
        )

        # PHASE 2: Parallel Reasoning Tracks
        # Track 1: Symbolic (Code-based solution)
        symbolic_task = self.programmer(
            instruction=f"""Generate Python code to solve the decomposed subproblems.
            Context: {decomposition}
            Requirements:
            - Define all unit conversions explicitly (e.g., inches to feet)
            - Use assert statements to validate dimensional consistency
            - Handle edge cases (negative values, zero division)
            - Return ONLY the final numerical answer as a float or int
            - Include comments mapping code to subproblem IDs""",
            context="",
            max_retries=3
        )

        # Track 2: Semantic (Step-by-step narrative)
        semantic_draft = await self.generate(
            instruction=f"""Solve the problem step-by-step in natural language.
            Context: {decomposition}
            Requirements:
            - Show all intermediate calculations
            - Justify each operation with reference to the problem text
            - Track units at every step
            - Box the final answer at the end""",
            context=""
        )
        
        semantic_refined = await self.revise(
            instruction="""Improve the solution:
            - Verify all arithmetic calculations
            - Ensure unit consistency throughout
            - Highlight any assumptions made
            - Format final answer as: \\boxed{{number}}""",
            context=semantic_draft
        )

        # Track 3: Verification (Constraint & Unit Audit)
        verification = await self.generate(
            instruction=f"""Audit the problem for:
            - All numerical values and their units
            - Physical/logical constraints (e.g., non-negative, integer-only)
            - Potential misinterpretations (ambiguous phrases, cultural units)
            - Required unit conversions
            Return a validation report with 'PASS' or 'FAIL' for each check.""",
            context=""
        )

        # Run all tracks concurrently
        symbolic_result, _ = await asyncio.gather(
            symbolic_task,
            asyncio.sleep(0)  # Dummy to satisfy gather with one awaitable
        )

        # PHASE 3: Ensemble & Synthesis
        candidate_solutions = [symbolic_result, semantic_refined, verification]
        synthesized = await self.ensemble(
            instruction="""Synthesize the three solution tracks:
            1. SYMBOLIC: Code-generated answer (prioritize if units/constraints pass)
            2. SEMANTIC: Step-by-step narrative (fallback if symbolic fails)
            3. VERIFICATION: Constraint audit (override if critical error found)
            
            Decision rules:
            - If verification reports FAIL, trigger refinement loop
            - If symbolic and semantic agree, return that answer
            - If conflict, prefer symbolic if unit conversions are explicit
            - Extract ONLY the final numerical value as a string (no units, no text)
            
            Return format: "ANSWER: <number>" """,
            contexts_list=candidate_solutions
        )

        # PHASE 4: Adaptive Refinement (if needed)
        if "FAIL" in synthesized or "conflict" in synthesized.lower():
            # Refine decomposition with error context
            refined_decomposition = await self.revise(
                instruction=f"""Re-decompose the problem considering these errors:
                {synthesized}
                Focus on:
                - Clarifying ambiguous phrases
                - Explicit unit conversion steps
                - Breaking complex operations into simpler ones""",
                context=str(decomposition)
            )

            # Re-run symbolic track with refined context
            refined_symbolic = await self.programmer(
                instruction=f"""Solve with refined decomposition:
                {refined_decomposition}
                Requirements:
                - More verbose unit tracking
                - Intermediate assertion checks
                - Return only final number""",
                context="",
                max_retries=2
            )
            final_answer = refined_symbolic
        else:
            final_answer = synthesized

        # PHASE 5: Answer Extraction & Sanitization
        # Extract number from any format (handles "ANSWER: 280", "\\boxed{280}", etc.)
        match = re.search(r"[-+]?\d*\.\d+|\d+", final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return raw if no number found (shouldn't happen)
            return final_answer.strip()