# Workflow ID: mgsmbn_124_0
# Benchmark: mgsmbn
# Data Indices: [22, 48]

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

        # STEP 1: META-ANALYSIS - Understand problem structure, type, and requirements
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive meta-analysis of this Bengali math word problem. Answer the following in structured detail:
            1. Problem Type Classification: Is this a ratio, rate, distribution, comparison, sequential operation, or multi-entity tracking problem? Or a hybrid?
            2. Key Entities: List all people, objects, or quantities mentioned with their associated values.
            3. Relationships: Describe mathematical or logical relationships between entities (ratios, sums, differences, proportions, time sequences).
            4. Unknown: What exactly is being asked? Be specific.
            5. Constraints: Are there implicit or explicit constraints? (e.g., non-negative, integer-only, unit consistency)
            6. Suggested Strategies: Recommend 2-3 potential solution approaches based on problem structure.
            7. Red Flags: Any ambiguous phrasing, missing information, or potential traps?
            
            Format your response clearly with numbered sections. This analysis will guide all subsequent solution attempts.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION - Three distinct solution approaches
        strategy_instructions = [
            """Solve this problem using DIRECT ARITHMETIC & SEQUENTIAL REASONING:
            - Translate the Bengali narrative into a step-by-step arithmetic procedure.
            - Perform calculations in the order events occur or as logically sequenced.
            - Show intermediate values and units at each step.
            - Do not use algebraic variables unless absolutely necessary.
            - Focus on concrete, procedural calculation.
            - Double-check unit consistency and contextual plausibility (e.g., no negative ages).""",
            
            """Solve this problem using ALGEBRAIC MODELING & EQUATION BUILDING:
            - Define variables for unknowns and key quantities.
            - Translate relationships into equations or proportions.
            - Solve symbolically first, then substitute known values.
            - Show equation setup, simplification, and solution steps.
            - Verify that final answer satisfies all original conditions.
            - Emphasize structural relationships over procedural steps.""",
            
            """Solve this problem using UNIT TRACKING & CONTEXTUAL SIMULATION:
            - Treat the problem as a real-world scenario. Track units (টাকা, ঘণ্টা, জিনিস) rigorously.
            - Simulate the scenario chronologically or causally.
            - Calculate totals, rates, or distributions by modeling the described situation.
            - Pay special attention to time-based or rate-based elements.
            - Ensure final answer makes sense in real-world context (e.g., fractional people only if allowed)."""
        ]

        # Generate three solution attempts in parallel
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_instructions]
        )

        # STEP 3: PARALLEL REVISION - Critique and correct each solution attempt
        critique_instructions = [
            f"""Critically review Solution Attempt {i+1} below. Your task:
            - Check for arithmetic errors or calculation mistakes.
            - Verify unit consistency throughout (e.g., hours not converted to minutes improperly).
            - Ensure logical flow matches problem narrative.
            - Confirm answer satisfies all constraints and question requirements.
            - Assess contextual plausibility (e.g., no negative quantities unless allowed).
            - If errors found, correct them and explain the fix.
            - If approach is fundamentally flawed, explain why and suggest alternative.
            - Output should be the corrected solution or a clear explanation of why it's invalid.
            
            Solution Attempt {i+1}:
            {attempt}"""
            for i, attempt in enumerate(solution_attempts)
        ]

        revised_solutions = await asyncio.gather(
            *[self.revise(instruction=instr, context=attempt) for instr, attempt in zip(critique_instructions, solution_attempts)]
        )

        # STEP 4: ENSEMBLE SYNTHESIS - Combine the best elements into final answer
        final_answer = await self.ensemble(
            instruction="""You are given three revised solution attempts for a Bengali math word problem. Your task:
            1. Compare all three solutions. Identify agreements and discrepancies.
            2. Evaluate each solution based on:
               - Mathematical correctness
               - Unit consistency
               - Logical alignment with problem narrative
               - Handling of constraints and edge cases
               - Clarity and completeness of reasoning
            3. Synthesize the most accurate answer. If two solutions agree and one differs, explain why the outlier is wrong.
            4. If all three differ, construct a fourth solution by combining valid elements from each.
            5. Output ONLY the final numerical answer as a single number (integer or decimal). No explanation, no units, no text.
            
            IMPORTANT: Your output must be a single numerical value that directly answers the original question.""",
            contexts_list=revised_solutions
        )

        # STEP 5: PROGRAMMATIC VERIFICATION - Computational truth check
        verified_result = await self.programmer(
            instruction=f"""Verify the following answer by writing and executing Python code:
            Final Answer to Verify: {final_answer}
            
            Instructions:
            1. Extract key numerical values and relationships from the ORIGINAL PROBLEM.
            2. Model the problem mathematically in Python.
            3. Perform calculations to compute the answer from first principles.
            4. Output ONLY the final numerical result (as int or float).
            5. If your result differs from the provided answer, output your computed result (do not explain).
            
            Note: The original problem is available internally. Do not rely on previous analyses - work from the original text.""",
            context=""
        )

        # STEP 6: RECONCILIATION (if needed) - Resolve discrepancies between linguistic and computational results
        # Clean both results to extract only numerical values
        def extract_number(text):
            import re
            match = re.search(r'[-+]?\d*\.?\d+', str(text))
            return float(match.group()) if match else None

        final_num = extract_number(final_answer)
        verified_num = extract_number(verified_result)

        if final_num is not None and verified_num is not None and abs(final_num - verified_num) > 1e-6:
            # Discrepancy found - reconcile
            reconciliation = await self.revise(
                instruction=f"""RECONCILIATION REQUIRED: Two conflicting results exist.
            Linguistic/Ensemble Result: {final_answer}
            Programmatic Verification Result: {verified_result}
            
            Your task:
            1. Compare both results and their underlying reasoning.
            2. Determine whether the error lies in:
               - Misinterpretation of the Bengali problem text (linguistic error)
               - Incorrect mathematical modeling or calculation (computational error)
               - Unit conversion or contextual misunderstanding
            3. Correct the error and output ONLY the final numerical answer.
            4. Do not output any explanation - only the number.
            
            Be meticulous. The original problem is available internally for reference.""",
                context=f"Linguistic Result: {final_answer}\n\nProgrammatic Result: {verified_result}"
            )
            return str(reconciliation).strip()
        else:
            # No significant discrepancy - return verified result (more trustworthy)
            return str(verified_result).strip()