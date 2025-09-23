# Workflow ID: mgsmbn_78_0
# Benchmark: mgsmbn
# Data Indices: [119]

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

        # PHASE 1: SEMANTIC DECOMPOSITION - Understand entities, quantities, relationships
        decomposition_instruction = """
        Perform a detailed semantic decomposition of this Bengali math word problem. Identify:
        1. All named entities (people, objects, containers) and their roles.
        2. All numerical values and EXACTLY what they quantify (e.g., "500টি টুকরো" → quantity=500, unit=টুকরো, object=লেগো).
        3. All comparative or proportional relationships (e.g., "3 গুণ", "1/4 ভাগ") with explicit base references.
        4. Temporal or causal sequences (what happens first, next, etc.).
        5. Implicit constraints (e.g., non-negative, integer-only, real-world plausibility).
        
        Output as a structured JSON-like list with clear mappings. Be exhaustive and precise.
        """
        decomposition = await self.generate(instruction=decomposition_instruction, context="")

        # PHASE 2: PARALLEL STRATEGY GENERATION - Explore multiple solution approaches
        strategy_instructions = [
            """
            Strategy 1: Algebraic Modeling
            Convert the problem into algebraic equations. Define variables for unknowns. 
            Express all relationships as equations. Solve symbolically. Show step-by-step derivation.
            Prioritize exact symbolic manipulation over numerical approximation.
            """,
            """
            Strategy 2: Step-by-Step Arithmetic
            Solve numerically by breaking into sequential arithmetic operations. 
            For each step: state operation, inputs, output, and unit. Track intermediate results.
            Handle fractions/decimals precisely. Verify each step against problem constraints.
            """,
            """
            Strategy 3: Unit-Aware Computation
            Treat all quantities with explicit units. Convert units if needed. 
            Use dimensional analysis to verify operations. Reject steps that violate unit consistency.
            Output final answer with correct unit and format.
            """
        ]

        # Generate 3 parallel solution attempts
        strategy_tasks = [
            self.generate(instruction=instr, context=decomposition)
            for instr in strategy_instructions
        ]
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: CONSTRAINT-AWARE REVISION - Validate against real-world plausibility
        revised_strategies = []
        for i, strategy in enumerate(raw_strategies):
            revision_instruction = f"""
            CRITICALLY REVISE this solution attempt (Strategy {i+1}):
            1. Check for mathematical errors in calculations or logic.
            2. Verify against implicit constraints: no negative quantities, no fractional people/objects unless specified.
            3. Ensure unit consistency throughout (e.g., টাকা, ঘণ্টা, টুকরো).
            4. Confirm the final answer matches the problem's required format (integer/decimal).
            5. If any step is ambiguous or unjustified, flag it and propose correction.
            
            Output the revised solution with corrections clearly marked. If fundamentally flawed, output "INVALID".
            """
            revised = await self.revise(instruction=revision_instruction, context=strategy)
            revised_strategies.append(revised)

        # PHASE 4: ENSEMBLE SYNTHESIS - Select or merge best solutions
        ensemble_instruction = """
        You are given 3 revised solution attempts for a Bengali math problem. 
        Your task:
        1. Compare all valid solutions (ignore any marked "INVALID").
        2. If all valid solutions agree numerically, select any and output it.
        3. If they disagree, identify the most consistent with problem constraints and decomposition.
        4. If no clear winner, synthesize a new solution by combining strongest elements from each.
        5. Output ONLY the final numerical answer (integer or decimal) with no explanation.
        
        CRITICAL: The answer must be a single number. Extract it precisely.
        """
        consensus_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=revised_strategies
        )

        # PHASE 5: PROGRAMMATIC VERIFICATION - Generate and execute code for precision
        code_instruction = f"""
        Based on the problem decomposition and consensus solution, generate Python code that:
        1. Computes the answer programmatically using exact arithmetic.
        2. Includes assertions to validate against problem constraints (e.g., positivity, integer checks).
        3. Outputs ONLY the final numerical result (no text, no units).
        
        Use the following context for accuracy:
        Decomposition: {decomposition}
        Consensus: {consensus_answer}
        """
        try:
            code_result = await self.programmer(instruction=code_instruction, context="")
            # Extract number from code output (handles cases where code prints extra text)
            code_number = re.search(r'[-+]?\d*\.\d+|\d+', code_result)
            if code_number:
                code_answer = code_number.group(0)
            else:
                code_answer = consensus_answer  # Fallback if parsing fails
        except Exception:
            code_answer = consensus_answer  # Fallback on any error

        # PHASE 6: CROSS-VERIFICATION & FINAL OUTPUT
        verification_instruction = f"""
        FINAL VERIFICATION:
        Compare two answers:
        - Consensus Answer: {consensus_answer}
        - Code Answer: {code_answer}
        
        If they match exactly, output the number.
        If they differ, re-examine the decomposition and constraints. 
        Choose the answer that best satisfies:
        1. Mathematical correctness
        2. Unit consistency
        3. Real-world plausibility
        
        Output ONLY the final numerical value (integer or decimal). Nothing else.
        """
        final_answer = await self.revise(
            instruction=verification_instruction,
            context=f"Decomposition: {decomposition}"
        )

        # Ensure output is clean number (remove any accidental text)
        clean_answer = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        return clean_answer.group(0) if clean_answer else final_answer.strip()