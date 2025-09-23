# Workflow ID: limr_140_0
# Benchmark: limr
# Data Indices: [309, 104]

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
        import json

        # --- PHASE 1: Problem Classification & Decomposition ---
        classification = await self.generate(
            instruction="""Thoroughly classify this mathematical problem:
            1. Identify the primary mathematical domain (e.g., geometry, number theory, combinatorics, algebra, optimization).
            2. List all secondary domains that may be relevant.
            3. Extract all numerical constants, variables, constraints, and implicit assumptions.
            4. Predict the most likely solution strategies (e.g., modular arithmetic, coordinate geometry, generating functions).
            5. Estimate the number of reasoning steps required.
            Format your response as a structured JSON-like summary.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal, atomic subproblems:
            - Each subproblem should be independently solvable and necessary for the final answer.
            - Specify the mathematical nature of each subproblem (algebraic, geometric, combinatorial, etc.).
            - Define dependencies between subproblems (which must be solved before others).
            - Ensure the decomposition covers all aspects of the problem without redundancy.
            - Use the following classification to guide your decomposition: {classification}
            Return a list of subproblem dictionaries with 'id', 'description', and 'dependencies'.""",
            context=""
        )

        # --- PHASE 2: Parallel Strategy Exploration ---
        strategy_instructions = [
            f"""Solve using ALGEBRAIC & EQUATIONAL REASONING:
            - Manipulate given equations symbolically.
            - Factor, substitute, or transform expressions to isolate variables.
            - Use the problem classification: {classification}
            - Reference subproblems: {[sp['id'] for sp in decomposition]}
            - Derive the final integer answer between 000 and 999.""",
            
            f"""Solve using NUMBER THEORETIC & MODULAR REASONING:
            - Consider divisibility, prime factors, modular constraints.
            - Bound variables using inequalities or modular residues.
            - Use the problem classification: {classification}
            - Reference subproblems: {[sp['id'] for sp in decomposition]}
            - Derive the final integer answer between 000 and 999.""",
            
            f"""Solve using COMBINATORIAL & COUNTING PRINCIPLES:
            - Model as permutations, combinations, or probability spaces.
            - Use generating functions or recursive relations if applicable.
            - Use the problem classification: {classification}
            - Reference subproblems: {[sp['id'] for sp in decomposition]}
            - Derive the final integer answer between 000 and 999.""",
            
            f"""Solve using GEOMETRIC & COORDINATE-BASED REASONING:
            - Assign coordinates, use vectors, or apply geometric theorems.
            - Calculate distances, angles, or areas as needed.
            - Use the problem classification: {classification}
            - Reference subproblems: {[sp['id'] for sp in decomposition]}
            - Derive the final integer answer between 000 and 999."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # --- PHASE 3: Validation & Synthesis ---
        revised_attempts = await asyncio.gather(
            *[self.revise(
                instruction="""Critically revise this solution:
                - Check for logical gaps, algebraic errors, or violated constraints.
                - Ensure all steps are justified and lead to the final answer.
                - If flawed, correct it. If correct, formalize the argument.
                - Extract and bold the final integer answer (000-999).""",
                context=attempt
            ) for attempt in strategy_attempts]
        )

        synthesized = await self.ensemble(
            instruction="""Synthesize the best solution from these attempts:
            - Select the most rigorous, complete, and correct derivation.
            - If multiple are valid, merge their strongest insights.
            - Resolve any contradictions by re-deriving contested steps.
            - Output ONLY the final integer answer (000-999) in bold, e.g., **427**.
            - If uncertain, state 'UNCERTAIN' and explain why.""",
            contexts_list=revised_attempts
        )

        # --- PHASE 4: Computational Verification ---
        code_result = await self.programmer(
            instruction=f"""Implement and execute the winning solution strategy:
            - Translate the mathematical derivation into precise Python code.
            - Compute the exact integer answer (000-999).
            - Avoid floating-point arithmetic; use integers or fractions.
            - Validate against problem constraints.
            - If multiple answers are possible, find the one matching the synthesized result.
            - Output only the integer, nothing else.
            Context from synthesis: {synthesized}""",
            context=synthesized,
            max_retries=3
        )

        # --- FINAL VALIDATION & OUTPUT ---
        final_answer = await self.ensemble(
            instruction="""Reconcile analytical and computational results:
            - If the synthesized answer and code result match, output that integer.
            - If they conflict, re-examine the derivation for errors and output the corrected answer.
            - Ensure the answer is an integer between 000 and 999.
            - Output ONLY the final integer, no explanation.""",
            contexts_list=[synthesized, code_result]
        )

        # Extract integer from final answer (robust parsing)
        import re
        match = re.search(r'\b\d{1,3}\b', final_answer)
        if match:
            return match.group(0).zfill(3)  # Ensure 3-digit format
        else:
            # Fallback: return first 3-digit number from any attempt
            all_text = " ".join([synthesized, code_result] + strategy_attempts)
            fallback_match = re.search(r'\b\d{1,3}\b', all_text)
            if fallback_match:
                return fallback_match.group(0).zfill(3)
            else:
                return "000"  # Ultimate fallback