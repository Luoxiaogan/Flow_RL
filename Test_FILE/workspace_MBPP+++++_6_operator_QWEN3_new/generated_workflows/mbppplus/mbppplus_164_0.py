# Workflow ID: mbppplus_164_0
# Benchmark: mbppplus
# Data Indices: [266, 241]

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

        # PHASE 1: SEMANTIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its core semantic components:
            1. What is the exact input structure? (e.g., list of integers, string, tuple)
            2. What is the precise output expectation? (type, format, constraints)
            3. What invariant, condition, or transformation links input to output?
            4. What are the implicit edge cases? (empty inputs, single elements, duplicates, type boundaries)
            5. What category does this problem belong to? (counting, searching, transforming, validating, etc.)
            Return structured subproblems that capture the mathematical or logical essence, not just surface description.""",
            context=""
        )

        # Convert decomposition to readable context
        decomposition_context = "\n".join([
            f"Subproblem {item['id']}: {item['description']} (Depends on: {item.get('dependencies', 'none')})"
            for item in decomposition
        ])

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Based on the problem decomposition, generate a solution strategy that treats this as a COUNTING problem.
            Focus on: frequency analysis, parity checks, aggregation of properties.
            Example: counting odd numbers, counting occurrences, summing conditions.
            Ignore surface-level verbs like 'find minimum' — focus on underlying mathematical invariant.""",
            
            """Based on the problem decomposition, generate a solution strategy that treats this as a SEARCHING/TRANSFORMATION problem.
            Focus on: iterating and selecting elements, applying filters, mapping values.
            Consider: early termination, index-based logic, in-place transformations.
            Assume the problem may be misdirection — e.g., 'minimum' might mean 'first satisfying condition'.""",
            
            """Based on the problem decomposition, generate a solution strategy that treats this as a SET/LOGIC problem.
            Focus on: set operations, uniqueness, membership, XOR patterns, mathematical identities.
            Leverage: properties like commutativity, idempotence, or parity invariants.
            Ideal for problems where order doesn't matter or duplicates cancel out."""
        ]

        strategy_contexts = await asyncio.gather(*[
            self.generate(instruction=instr, context=decomposition_context)
            for instr in strategy_instructions
        ])

        # PHASE 3: PARALLEL CODE SYNTHESIS
        code_instructions = [
            f"""Generate Python code that implements the following strategy:
            {strategy}
            
            STRICT REQUIREMENTS:
            - Use EXACT function signature from problem.
            - Handle edge cases: empty inputs, single elements, duplicates, type mismatches.
            - Return correct data type (int, list, tuple, etc.) as implied by problem.
            - No extra output or print statements.
            - Code must be minimal and efficient where possible.
            - Include defensive checks only if logically necessary.
            
            If implementation fails, retry up to 3 times with corrections.""",
            f"""Generate Python code that implements the following strategy:
            {strategy_contexts[1]}
            
            STRICT REQUIREMENTS:
            - Use EXACT function signature from problem.
            - Handle edge cases: empty inputs, single elements, duplicates, type mismatches.
            - Return correct data type (int, list, tuple, etc.) as implied by problem.
            - No extra output or print statements.
            - Code must be minimal and efficient where possible.
            - Include defensive checks only if logically necessary.
            
            If implementation fails, retry up to 3 times with corrections.""",
            f"""Generate Python code that implements the following strategy:
            {strategy_contexts[2]}
            
            STRICT REQUIREMENTS:
            - Use EXACT function signature from problem.
            - Handle edge cases: empty inputs, single elements, duplicates, type mismatches.
            - Return correct data type (int, list, tuple, etc.) as implied by problem.
            - No extra output or print statements.
            - Code must be minimal and efficient where possible.
            - Include defensive checks only if logically necessary.
            
            If implementation fails, retry up to 3 times with corrections."""
        ]

        code_attempts = await asyncio.gather(*[
            self.programmer(instruction=instr, context="", max_retries=3)
            for instr in code_instructions
        ])

        # PHASE 4: ENSEMBLE SELECTION
        selected_code = await self.ensemble(
            instruction="""Select the BEST solution from the candidates below based on:
            1. CORRECTNESS: Matches function signature and handles edge cases explicitly.
            2. ROBUSTNESS: No assumptions about input validity; graceful handling of boundaries.
            3. EFFICIENCY: Avoids unnecessary nested loops or redundant operations where possible.
            4. CLARITY: Logic is easy to follow and matches the problem's inferred intent.
            5. TYPE SAFETY: Returns exactly the expected type (int, not float; tuple, not list, etc.).
            
            DO NOT select based on which runs fastest — select based on which is most likely to pass rigorous hidden test cases.
            Return ONLY the raw code block (no markdown, no explanation).""",
            contexts_list=code_attempts
        )

        # PHASE 5: FINAL REVISION & HARDENING
        final_code = await self.revise(
            instruction="""Revise the selected code to ensure:
            1. EXACT function signature is preserved (parameter names, order, return type).
            2. All edge cases are handled explicitly (even if not in original code):
               - Empty inputs
               - Single-element inputs
               - All elements identical
               - Negative numbers or zero if applicable
            3. Type consistency: if problem implies integer return, ensure no float conversion.
            4. Remove any debugging prints or extra outputs.
            5. Simplify logic without changing behavior (e.g., replace verbose conditionals with mathematical equivalents).
            6. Match reference style: minimal, no extra whitespace, no comments unless critical.
            
            Output ONLY the final code block — nothing else.""",
            context=selected_code
        )

        # Extract just the code block if wrapped in markdown
        code_block_match = re.search(r'