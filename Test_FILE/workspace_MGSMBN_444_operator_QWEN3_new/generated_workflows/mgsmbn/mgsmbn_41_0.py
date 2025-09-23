# Workflow ID: mgsmbn_41_0
# Benchmark: mgsmbn
# Data Indices: [170, 172]

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

        # STEP 1: PARALLEL SEMANTIC DECOMPOSITION
        literal_extraction = await self.generate(
            instruction="""Extract all explicit numerical values, named entities, and direct relationships from the Bengali problem text. 
            Format as:
            - Numbers: [value] [unit if any] → [what it represents]
            - Entities: [person/object] → [role or description]
            - Direct Actions: [verb phrase] → [mathematical implication]
            Be literal. Do not infer. Just report what is explicitly stated.""",
            context=""
        )

        relational_modeling = await self.generate(
            instruction="""Model the implicit relationships and operations. Identify:
            - What mathematical operations are implied by verbs and context? (e.g., 'হাঁটে' with speed and distance implies multiplication; 'কিনতে চায়' with multiple items implies addition)
            - What is the sequence of operations? (chronological, causal, or conditional)
            - What are the hidden constraints? (e.g., 'around the park' implies perimeter; 'per hour' implies rate)
            Structure your output as a dependency graph in text form: Step 1 → Step 2 → ... → Final Answer""",
            context=""
        )

        goal_inference = await self.generate(
            instruction="""Infer the exact mathematical goal. Ask:
            - What is the unknown we are solving for? (time? cost? quantity?)
            - What units must the answer have?
            - Are there real-world constraints? (e.g., no negative people, must be integer if counting items)
            - Is this a rate, proportion, distribution, or comparison problem?
            Output in format: GOAL: [description]; UNITS: [unit]; CONSTRAINTS: [list]; TYPE: [category]""",
            context=""
        )

        # STEP 2: SYNTHESIZE INTO UNIFIED PROBLEM MODEL
        problem_model = await self.ensemble(
            instruction="""Synthesize the three perspectives into a single, coherent problem model. Resolve contradictions. Fill gaps. Enforce unit consistency. 
            Your output must include:
            1. Known Quantities (with units and sources)
            2. Unknown (what we solve for, with expected unit)
            3. Required Operations (sequence and type)
            4. Constraints (explicit and implicit)
            5. Problem Type Classification (rate, proportion, distribution, comparison, multi-step)
            Format as a structured JSON-like block in plain text.""",
            contexts_list=[literal_extraction, relational_modeling, goal_inference]
        )

        # STEP 3: CONDITIONAL STRATEGY SELECTION
        strategy_analysis = await self.generate(
            instruction=f"""Based on the problem model:
            {problem_model}
            
            Select the optimal solution strategy. Options:
            A) Step-by-Step Arithmetic: Best for sequential, rate, or distribution problems with clear numerical progression.
            B) Algebraic Modeling: Best for proportional, comparison, or multi-entity problems requiring equation setup.
            C) Hybrid: When both are equally valid.
            
            Justify your choice. Then, outline the exact steps for the chosen strategy, including intermediate variables and unit tracking.
            Output format: STRATEGY: [A/B/C]; JUSTIFICATION: [text]; STEP_PLAN: [numbered steps]""",
            context=problem_model
        )

        # STEP 4: PARALLEL SOLUTION GENERATION
        arithmetic_solution = await self.generate(
            instruction=f"""Execute a STEP-BY-STEP ARITHMETIC solution. 
            Problem Model: {problem_model}
            Strategy Outline: {strategy_analysis}
            
            Requirements:
            - Show every calculation explicitly.
            - Track units at every step.
            - Verify intermediate results make sense (e.g., no negative time).
            - If you encounter ambiguity, state assumption and proceed.
            - Final answer must be a single numerical value (integer or decimal).""",
            context=problem_model
        )

        algebraic_solution = await self.generate(
            instruction=f"""Execute an ALGEBRAIC solution. 
            Problem Model: {problem_model}
            Strategy Outline: {strategy_analysis}
            
            Requirements:
            - Define variables for unknowns.
            - Write equations based on relationships.
            - Solve step-by-step with substitutions.
            - Track units and validate dimensional consistency.
            - Final answer must be a single numerical value (integer or decimal).""",
            context=problem_model
        )

        # STEP 5: CROSS-VALIDATION LOOP (max 2 iterations)
        solutions = [arithmetic_solution, algebraic_solution]
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Compare the two solutions:
                Solution 1 (Arithmetic): {solutions[0]}
                Solution 2 (Algebraic): {solutions[1]}
                
                Check for:
                - Numerical agreement (same final value?)
                - Unit consistency
                - Logical soundness of steps
                - Adherence to problem constraints
                
                If they disagree, identify which one is likely wrong and why. If both seem flawed, suggest corrections.
                Output: AGREEMENT: [yes/no]; ISSUES: [list]; RECOMMENDED_CORRECTIONS: [if any]""",
                context=f"{solutions[0]}\n\n{solutions[1]}"
            )

            if "no" not in validation.lower() or "disagree" not in validation.lower():
                break  # Solutions agree, no need to revise

            # Revise the more flawed solution
            if "arithmetic" in validation.lower():
                solutions[0] = await self.revise(
                    instruction=f"""Revise based on validation feedback:
                    {validation}
                    
                    Fix errors in logic, calculation, or unit handling. Maintain step-by-step clarity.
                    Final answer must be a single numerical value.""",
                    context=solutions[0]
                )
            else:
                solutions[1] = await self.revise(
                    instruction=f"""Revise based on validation feedback:
                    {validation}
                    
                    Fix errors in equation setup, variable definition, or solution steps.
                    Final answer must be a single numerical value.""",
                    context=solutions[1]
                )

        # STEP 6: FINAL ENSEMBLE AND ANSWER EXTRACTION
        final_answer = await self.ensemble(
            instruction="""Select the best final answer from the two solutions. Prioritize:
            1. Numerical correctness (validated by cross-check)
            2. Unit consistency
            3. Adherence to real-world constraints
            4. Clarity of derivation
            
            Then, extract ONLY the numerical value (integer or decimal). Strip all units, explanations, and text.
            If the value is fractional, preserve decimal precision as implied by the problem (e.g., money → 2 decimals; time → 1 decimal if needed).
            Output format: [number] (nothing else)""",
            contexts_list=solutions
        )

        # Clean and return final numerical answer
        # Extract first number from the response (defensive parsing)
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return raw if no number found (shouldn't happen)
            return final_answer.strip()