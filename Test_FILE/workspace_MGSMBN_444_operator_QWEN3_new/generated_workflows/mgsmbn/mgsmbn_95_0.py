# Workflow ID: mgsmbn_95_0
# Benchmark: mgsmbn
# Data Indices: [93, 80]

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

        # STEP 1: Extract entities, quantities, relationships with structured format
        extraction_instruction = """
        You are a meticulous Bengali math problem deconstructor. Your task:
        1. Identify ALL numerical values and their associated units (টাকা, পৃষ্ঠা, জোড়া, etc.)
        2. Identify ALL agents (people/objects) and their roles
        3. Map relationships: who did what to whom, with what quantities
        4. Identify the explicit question being asked
        5. Flag any potentially irrelevant information
        Format output as:
        [Entities]: ...
        [Quantities]: ...
        [Relationships]: ...
        [Target]: ...
        [Red Herrings]: ...
        """
        extraction = await self.generate(instruction=extraction_instruction, context="")

        # STEP 2: Classify problem type and select strategy
        classification_instruction = f"""
        Based on extracted structure:
        {extraction}

        Classify this problem into one primary type:
        - Sequential Operations (multiple dependent steps)
        - Rate/Time/Distance (speed, work rate, unit price)
        - Proportional (ratios, percentages, fractions)
        - Distribution (division, sharing, remainders)
        - Comparison (differences, "how many more")
        - Multi-entity Tracking (multiple actors with different values)

        Then, outline a step-by-step solving strategy that:
        - Lists required intermediate calculations
        - Specifies order of operations
        - Notes unit conversions or consistency checks needed
        - Highlights potential pitfalls (e.g., "don't forget to subtract first")

        Format as:
        [Type]: ...
        [Strategy]: 
        Step 1: ...
        Step 2: ...
        ...
        """
        strategy = await self.generate(instruction=classification_instruction, context=extraction)

        # STEP 3: Generate initial solution draft with explicit intermediates
        solution_draft_instruction = f"""
        Using this strategy:
        {strategy}

        And original extraction:
        {extraction}

        Generate a complete solution draft that:
        - Shows ALL intermediate calculations with units
        - Labels each step clearly (Step 1, Step 2, ...)
        - Performs arithmetic explicitly (e.g., "6 pairs × $60/pair = $360")
        - States the final answer numerically at the end, prefixed by "FINAL_ANSWER: "

        Example format:
        Step 1: Total pairs = 3 children × 2 pairs/child = 6 pairs
        Step 2: Total cost = 6 pairs × $60/pair = $360
        FINAL_ANSWER: 360
        """
        draft = await self.generate(instruction=solution_draft_instruction, context=strategy)

        # STEP 4: Parallel validation - spawn two validators
        async def validate_unit_consistency(context):
            return await self.revise(
                instruction="""
                You are a unit consistency auditor. Check:
                1. Are all multiplications/divisions dimensionally sound? (e.g., pages/day × days = pages)
                2. Are units preserved or converted correctly?
                3. Is the final answer in the expected unit?
                4. Flag any unit mismatches or unexplained unit drops.
                If no issues, respond "UNIT_CHECK_PASSED". Otherwise, list specific fixes needed.
                """,
                context=context
            )

        async def validate_logical_consistency(context):
            return await self.revise(
                instruction="""
                You are a logical constraint validator. Check:
                1. Do intermediate values make real-world sense? (no negative pages, fractional people unless specified)
                2. Are all given numbers used appropriately? Any ignored?
                3. Does the sequence of operations respect chronological or causal order?
                4. Are there alternative interpretations that might change the answer?
                If no issues, respond "LOGIC_CHECK_PASSED". Otherwise, list specific concerns.
                """,
                context=context
            )

        # Run validators in parallel
        unit_validation, logic_validation = await asyncio.gather(
            validate_unit_consistency(draft),
            validate_logical_consistency(draft)
        )

        # Conditional refinement loop (max 2 iterations)
        current_draft = draft
        for iteration in range(2):
            issues = []
            if "UNIT_CHECK_PASSED" not in unit_validation:
                issues.append(f"Unit issues: {unit_validation}")
            if "LOGIC_CHECK_PASSED" not in logic_validation:
                issues.append(f"Logic issues: {logic_validation}")
            
            if not issues:
                break  # Validation passed, exit loop
            
            # Revise draft based on combined feedback
            revision_instruction = f"""
            Revise the solution draft to address these issues:
            {'; '.join(issues)}

            Requirements:
            - Keep all correct intermediate steps
            - Fix only the flagged issues
            - Maintain explicit unit tracking
            - Re-output in same format with FINAL_ANSWER: at end
            """
            current_draft = await self.revise(instruction=revision_instruction, context=current_draft)
            
            # Re-validate if this wasn't the last iteration
            if iteration < 1:  # Don't validate after final iteration
                unit_validation, logic_validation = await asyncio.gather(
                    validate_unit_consistency(current_draft),
                    validate_logical_consistency(current_draft)
                )

        # STEP 5: Final ensemble - if we have multiple versions, pick best
        candidates = [current_draft]
        # If original draft was different and passed validation, include it
        if current_draft != draft and "UNIT_CHECK_PASSED" in unit_validation and "LOGIC_CHECK_PASSED" in logic_validation:
            candidates.append(draft)

        final_answer = await self.ensemble(
            instruction="""
            You are selecting the most reliable final answer. Criteria:
            1. Prefer answers with explicit, unit-consistent intermediate steps
            2. Prefer answers that address all validation concerns
            3. Extract ONLY the numerical value after "FINAL_ANSWER: "
            4. If multiple are valid, pick the one with clearest reasoning
            5. Output ONLY the number, nothing else.
            """,
            contexts_list=candidates
        )

        # Clean and return final answer
        # Extract number from final_answer (handles cases where ensemble might include text)
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return final_answer.strip()