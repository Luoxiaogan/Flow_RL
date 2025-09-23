# Workflow ID: mgsmbn_77_0
# Benchmark: mgsmbn
# Data Indices: [134, 144]

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

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify it based on:
            1. Primary mathematical structure: Is it sequential spending, proportional allocation, rate-based, distribution, comparison, or multi-entity tracking?
            2. Required operations: What arithmetic, algebraic, or proportional reasoning is needed?
            3. Key entities: Identify all actors, objects, and numerical values with their roles.
            4. Hidden steps: Are there implicit calculations or unstated dependencies?
            5. Unit types: What units are involved (টাকা, ঘণ্টা, etc.) and must be preserved?
            6. Answer constraints: Must the answer be integer? Non-negative? Within a certain range?
            Output a structured classification with clear headings for each category.""",
            context=""
        )

        # PHASE 2: ENTITY & RELATIONSHIP EXTRACTION
        extraction = await self.generate(
            instruction=f"""Based on the classification:
            {classification}

            Now extract all mathematical relationships with precision:
            - List every numerical value and what it quantifies (e.g., "€1090 = cost of computer")
            - Map dependencies (e.g., "donation = 1/2 * (salary - rent - fuel)")
            - Identify chronological or logical order of operations
            - Note any constraints (e.g., "remainder cannot be negative")
            Format as a numbered list of equations or relationships, with Bengali terms preserved but annotated with mathematical meaning.""",
            context=classification
        )

        # PHASE 3: PARALLEL SOLUTION DRAFTING (3 DIVERSE APPROACHES)
        draft_instructions = [
            f"""Solve using CHRONOLOGICAL ORDER:
            Follow the sequence of events as described in the Bengali text.
            - Start with initial value
            - Apply each transaction/operation in narrative order
            - Track intermediate balances/results
            - Show all arithmetic steps explicitly
            Classification context: {classification}
            Extracted relationships: {extraction}""",
            
            f"""Solve using ALGEBRAIC MODELING:
            Define variables for unknowns.
            Build equations from extracted relationships.
            Solve symbolically first, then substitute numbers.
            Verify dimensional consistency at each step.
            Classification context: {classification}
            Extracted relationships: {extraction}""",
            
            f"""Solve using UNIT-TRACKING & PROPORTIONAL REASONING:
            Treat all values as quantities with units.
            Cancel or convert units explicitly.
            For fractions/percentages, compute proportions step-by-step.
            Validate that final unit matches expected answer type.
            Classification context: {classification}
            Extracted relationships: {extraction}"""
        ]

        draft_tasks = [
            self.generate(instruction=instr, context="")
            for instr in draft_instructions
        ]
        solution_drafts = await asyncio.gather(*draft_tasks)

        # PHASE 4: VALIDATION & REVISION (2 ITERATIONS MAX)
        validated_drafts = []
        for draft in solution_drafts:
            current = draft
            for iteration in range(2):
                validation = await self.generate(
                    instruction=f"""CRITICALLY VALIDATE THIS SOLUTION:
                    - Check arithmetic accuracy (recalculate key steps)
                    - Verify unit consistency (no unit mismatches)
                    - Ensure contextual plausibility (no negative money, fractional people, etc.)
                    - Confirm alignment with extracted relationships: {extraction}
                    - Flag any logical gaps or unsupported assumptions
                    If errors found, describe them precisely. If clean, say "VALID". """,
                    context=current
                )
                if "VALID" in validation.upper() and "ERROR" not in validation.upper():
                    break
                current = await self.revise(
                    instruction=f"""REVISE BASED ON VALIDATION FEEDBACK:
                    Validation report: {validation}
                    - Fix all identified errors
                    - Add missing steps or justifications
                    - Preserve correct parts
                    - Maintain clear step-by-step reasoning
                    Original draft: {draft}""",
                    context=current
                )
            validated_drafts.append(current)

        # PHASE 5: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""SYNTHESIZE THE MOST ACCURATE ANSWER:
            You are given 3 independently validated solution drafts.
            - Compare their final numerical results
            - If all agree, output that number
            - If they disagree, analyze which approach best respects:
                a) The original Bengali problem's narrative
                b) Mathematical rigor (correct operations, unit handling)
                c) Real-world plausibility (non-negative, reasonable scale)
            - Resolve conflicts by prioritizing algebraic correctness over narrative flow
            - Extract ONLY the final numerical value (integer or decimal)
            - Remove all units, explanations, or text — output pure number""",
            contexts_list=validated_drafts
        )

        # PHASE 6: FINAL FORMATTING & CLEANUP
        cleaned_answer = await self.revise(
            instruction="""FINAL OUTPUT PREPARATION:
            You are given a candidate answer. Your task:
            - Extract ONLY the numerical value (integer or decimal)
            - Remove any surrounding text, units, or explanations
            - If decimal, remove trailing zeros (e.g., 77.00 → 77, but 77.5 stays 77.5)
            - Ensure no Bengali or English words remain
            - If multiple numbers, select the one that matches problem's final question
            Output must be a single, clean numerical string.""",
            context=final_answer
        )

        # Strip any remaining non-numeric characters except decimal point
        numeric_str = re.sub(r'[^\d.]', '', cleaned_answer)
        # Handle edge case where multiple decimals might exist (shouldn't, but safety)
        parts = numeric_str.split('.')
        if len(parts) > 2:
            numeric_str = parts[0] + '.' + ''.join(parts[1:])
        elif len(parts) == 2:
            # Remove trailing zeros from decimal part
            decimal_part = parts[1].rstrip('0')
            if decimal_part == '':
                numeric_str = parts[0]
            else:
                numeric_str = parts[0] + '.' + decimal_part

        return numeric_str