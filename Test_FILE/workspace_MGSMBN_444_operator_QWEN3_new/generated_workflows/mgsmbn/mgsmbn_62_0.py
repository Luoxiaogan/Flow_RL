# Workflow ID: mgsmbn_62_0
# Benchmark: mgsmbn
# Data Indices: [97, 149]

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

        # STEP 1: STRUCTURED ENTITY & RELATION EXTRACTION
        extraction = await self.generate(
            instruction="""Perform deep semantic extraction from the Bengali problem. Identify and structure:
            - All named entities (people, objects)
            - All explicit numerical values and their associated entities
            - All comparative relationships (e.g., "দ্বিগুণ", "অর্ধেক", "বেশি", "কম")
            - Temporal or conditional constraints
            Format as:
            ENTITIES:
            - [Entity]: [Quantity] [Unit/Description]
            RELATIONSHIPS:
            - [Entity A] [relation] [Entity B or Value]
            CONSTRAINTS:
            - [List any implicit or explicit constraints]
            Be exhaustive and precise. Preserve Bengali terms for relationships.""",
            context=""
        )

        # STEP 2: RESOLVE DERIVED QUANTITIES
        resolved = await self.generate(
            instruction=f"""Using the extracted structure:
            {extraction}

            Compute all derived quantities explicitly. For each relationship:
            - If "দ্বিগুণ" (double), multiply base by 2
            - If "অর্ধেক" (half), divide base by 2
            - If "অর্ধেকের বেশি" (more than half), consider both interpretations: (>0.5x) and (1.5x)
            - If "বেশি" (more) or "কম" (less), compute difference
            Show substitution steps. Maintain unit consistency.
            Output updated ENTITIES list with computed values.""",
            context=extraction
        )

        # STEP 3: PROBLEM CLASSIFICATION
        classification = await self.generate(
            instruction="""Classify this problem type based on structure and operations required:
            Options: 
            - Sequential Operations (multiple steps in order)
            - Proportional Reasoning (ratios, scaling, fractions)
            - Comparison (differences, "how many more")
            - Distribution (sharing, division, remainders)
            - Multi-entity Tracking (multiple agents with different quantities)
            Justify your choice with evidence from the text. Also identify required operations: +, -, ×, ÷, or combinations.""",
            context=resolved
        )

        # STEP 4: PARALLEL HYPOTHESIS GENERATION (for ambiguous phrases)
        # Detect if "অর্ধেকের বেশি" or similar ambiguous terms exist
        if "অর্ধেকের বেশি" in self.problem_text or "more than half" in self.problem_text.lower():
            hypotheses = await asyncio.gather(
                self.generate(
                    instruction=f"""Interpret "অর্ধেকের বেশি" as STRICTLY GREATER THAN HALF (>0.5x).
                    Using resolved entities: {resolved}
                    Compute final answer. Show all steps. Validate for integer/non-negative constraints.""",
                    context=resolved
                ),
                self.generate(
                    instruction=f"""Interpret "অর্ধেকের বেশি" as ONE AND A HALF TIMES (1.5x).
                    Using resolved entities: {resolved}
                    Compute final answer. Show all steps. Validate for integer/non-negative constraints.""",
                    context=resolved
                )
            )
            
            # STEP 5: ENSEMBLE BEST HYPOTHESIS
            answer_draft = await self.ensemble(
                instruction="""Select the most contextually and mathematically valid answer:
                - Prefer integer results over fractional
                - Ensure no negative quantities
                - Match real-world plausibility (e.g., whole fruits, not fractions)
                - Verify arithmetic accuracy
                Return ONLY the final numerical answer as an integer or decimal.""",
                contexts_list=hypotheses
            )
        else:
            # Direct solution path
            answer_draft = await self.generate(
                instruction=f"""Given classification: {classification}
                And resolved entities: {resolved}
                Compute the final answer using appropriate operations.
                Show step-by-step arithmetic.
                Validate: no negatives, units consistent, real-world plausible.
                Return ONLY the final numerical answer as an integer or decimal.""",
                context=resolved
            )

        # STEP 6: VALIDATION & REFINEMENT LOOP (max 2 iterations)
        refined_answer = answer_draft
        for _ in range(2):
            validation = await self.revise(
                instruction="""Critically validate this answer:
                - Recheck arithmetic for calculation errors
                - Ensure all entities and relationships from original problem are accounted for
                - Confirm no unit mismatches
                - Verify against constraints (non-negative, integer if required)
                If error found, correct it and return revised answer. If correct, return unchanged.
                Output ONLY the final numerical value.""",
                context=refined_answer
            )
            if validation.strip() == refined_answer.strip():
                break
            refined_answer = validation

        # STEP 7: FINAL SYNTHESIS & EXTRACTION
        final_answer = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this text:
            {refined_answer}
            Remove any units, explanations, or text. Return a clean number (integer or decimal).
            If multiple numbers, return the one that answers the main question.
            If none, return 0.""",
            context=refined_answer
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        try:
            # Convert to float then to int if whole number
            num = float(cleaned)
            return int(num) if num.is_integer() else num
        except:
            return 0  # Fallback