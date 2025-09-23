# Workflow ID: mgsmbn_96_0
# Benchmark: mgsmbn
# Data Indices: [175]

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

        # === STEP 1: PARALLEL EXTRACTION ===
        # Extract key components in parallel for robustness
        extraction_tasks = [
            self.generate(
                instruction="""Extract all numerical values and their contextual meaning. For each number:
                - What entity does it represent? (person, object, time, rate, etc.)
                - What unit is associated? (টাকা, বছর, জিনিস, etc.)
                - Is it a current value, future value, or rate?
                Format as bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all temporal markers and chronological relationships:
                - Words like 'পরে', 'আগে', 'এখন', 'তখন'
                - Phrases indicating time shifts ('তিন বছর পরে')
                - Sequence of events if any
                Return as a timeline or sequence list.""",
                context=""
            ),
            self.generate(
                instruction="""Map all relational phrases and multiplicative/divisive terms:
                - 'তিনগুণ', 'অর্ধেক', 'দ্বিগুণ', 'চেয়ে বেশি', 'চেয়ে কম'
                - Who/what is being compared?
                - Express relationships as equations if possible (A = 3×B)
                Format as relation pairs with operators.""",
                context=""
            )
        ]
        
        num_extraction, time_extraction, relation_extraction = await asyncio.gather(*extraction_tasks)

        # === STEP 2: SYNTHESIZE PROBLEM STATE ===
        problem_state = await self.generate(
            instruction=f"""Synthesize a complete problem model from these extractions:
            
            NUMERICAL DATA:
            {num_extraction}
            
            TEMPORAL DATA:
            {time_extraction}
            
            RELATIONAL DATA:
            {relation_extraction}
            
            Construct a unified model that includes:
            1. All entities with their current values
            2. All relationships as mathematical expressions
            3. Target unknown (what is being asked)
            4. Any time shifts to apply before final calculation
            5. Units to track throughout
            
            Format as a structured problem specification.""",
            context=f"{num_extraction}\n\n{time_extraction}\n\n{relation_extraction}"
        )

        # === STEP 3: CLASSIFY & ROUTE ===
        classification = await self.generate(
            instruction=f"""Classify this problem for solution strategy selection:
            
            PROBLEM STATE:
            {problem_state}
            
            Choose ONE primary type:
            - SEQUENTIAL: Multiple operations in specific order
            - PROPORTIONAL: Ratios, fractions, percentages, scaling
            - TEMPORAL: Age, time-based changes, future/past states
            - DISTRIBUTION: Sharing, division, remainders
            - COMPARISON: Differences, "how many more/less"
            
            Also flag if:
            - Requires hidden step (e.g., time shift not in direct calculation)
            - Has unit conversion
            - Needs intermediate rounding
            
            Return classification as: "TYPE: [type], FLAGS: [flag1, flag2, ...]""",
            context=problem_state
        )

        # === STEP 4: GENERATE SOLUTION ATTEMPT ===
        solution_draft = await self.generate(
            instruction=f"""Generate a complete step-by-step solution based on:
            
            PROBLEM STATE:
            {problem_state}
            
            CLASSIFICATION:
            {classification}
            
            Instructions:
            - Show ALL intermediate calculations explicitly
            - Apply time shifts BEFORE final operation if flagged
            - Track units at every step
            - Use variables for unknowns if needed
            - Box final answer at the end
            - If proportional, show ratio setup first
            - If sequential, number each step chronologically
            
            Format: Step 1: ... → Result: ...
                    Step 2: ... → Result: ...
                    ...
                    Final Answer: [boxed]""",
            context=problem_state
        )

        # === STEP 5: VALIDATE & REVISE (ITERATIVE) ===
        current_solution = solution_draft
        for iteration in range(3):  # Max 3 refinement loops
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                
                SOLUTION:
                {current_solution}
                
                Check for:
                1. Unit consistency throughout (no mixing টাকা with বছর)
                2. Temporal alignment (did we apply '3 years later' to ALL relevant entities?)
                3. Arithmetic accuracy (recompute key steps mentally)
                4. Contextual plausibility (no negative ages, fractional people unless allowed)
                5. Answer format (single number, integer or decimal as appropriate)
                
                If any issue found, describe EXACTLY what to fix.
                If perfect, respond with "VALIDATED: No issues found."""",
                context=current_solution
            )
            
            if "VALIDATED" in validation or "No issues found" in validation:
                break
                
            # Revise based on validation feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix these issues:
                
                VALIDATION FEEDBACK:
                {validation}
                
                Requirements:
                - Keep all correct parts unchanged
                - Only modify what's necessary
                - Maintain step-by-step clarity
                - Re-box final answer""",
                context=current_solution
            )

        # === STEP 6: FINAL EXTRACTION & OUTPUT ===
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution below.
            - It should be a single number (integer or decimal)
            - Remove any units, boxes, or explanatory text
            - If multiple numbers appear, choose the one that answers the original question
            - If uncertain, return the last computed number
            
            Return ONLY the number, nothing else.""",
            context=current_solution
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        
        # Handle edge case: if empty, return 0 (shouldn't happen with good validation)
        if not cleaned:
            cleaned = "0"
            
        return cleaned