# Workflow ID: mgsmbn_105_0
# Benchmark: mgsmbn
# Data Indices: [13]

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

        # === PHASE 1: SEMANTIC DECOMPOSITION ===
        entities_context = await self.generate(
            instruction="""Perform deep semantic decomposition of the Bengali word problem. Extract and structure the following:
            1. ENTITIES: All people, roles, objects mentioned (e.g., 'জিল', 'শিক্ষিকা', 'প্রশিক্ষক')
            2. QUANTITIES: All numbers with their semantic role (e.g., '35 ঘণ্টা' → hours_per_week_teaching)
            3. UNITS: All units of measurement (টাকা, ঘণ্টা, সপ্তাহ, etc.) and what they modify
            4. RELATIONSHIPS: Verbal phrases indicating mathematical operations (e.g., 'প্রতি ঘণ্টায়' → rate, 'মোট' → sum)
            5. GOAL: What is being asked? Rephrase the question mathematically.
            6. CONSTRAINTS: Explicit or implicit limitations (e.g., 'বার্ষিক' → multiply by 50 weeks)
            Format as a structured markdown list with clear headings. Be exhaustive.""",
            context=""
        )

        # === PHASE 2: COMPLEXITY CLASSIFICATION ===
        complexity_analysis = await self.generate(
            instruction=f"""Based on the semantic decomposition:
            {entities_context}

            Classify this problem into one of three tiers:
            - TIER 1: Single-step direct calculation (e.g., 5 × 10)
            - TIER 2: Multi-step with clear sequence (e.g., calculate weekly then annual)
            - TIER 3: Ambiguous, requires unit conversion, proportional reasoning, or hidden steps

            Also estimate confidence in classification (High/Medium/Low).
            Finally, recommend solution strategy: Direct, Parallel-Hypothesis, or Iterative-Validation.
            Output in JSON-like format: {{"tier": 1|2|3, "confidence": "High|Medium|Low", "strategy": "..."}}""",
            context=entities_context
        )

        # === PHASE 3: PARALLEL HYPOTHESIS GENERATION (Diamond Pattern) ===
        hypothesis_instructions = [
            """Generate Solution Hypothesis A: Focus on additive and multiplicative structure. 
            Assume all quantities are to be combined through + or ×. Explicitly state each operation and why.
            Format: Step 1: [action] → [calculation]. Step 2: ...""",
            
            """Generate Solution Hypothesis B: Focus on role-based or entity-based separation. 
            Treat each person/object as having independent calculations, then combine. Watch for 'and', 'or', 'each'.
            Format: For [Entity1]: [calc]. For [Entity2]: [calc]. Total: [combine].""",
            
            """Generate Solution Hypothesis C: Focus on rate and scaling. 
            Identify per-unit rates (per hour, per week) and scale to final unit (annual, total). Use dimensional analysis.
            Format: Rate = [value]/[unit]. Scale factor = [conversion]. Result = rate × scale."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context=entities_context) for instr in hypothesis_instructions]
        )

        # === PHASE 4: ENSEMBLE SYNTHESIS ===
        synthesized_hypothesis = await self.ensemble(
            instruction="""You are given three solution hypotheses for a Bengali math problem.
            Your task: Synthesize the most coherent, mathematically sound approach.
            Criteria:
            1. Which hypothesis best respects units and dimensional consistency?
            2. Which aligns with the semantic roles extracted earlier?
            3. Which handles edge cases (fractions, negatives, remainders) appropriately?
            4. Which has the clearest step-by-step justification?
            If all are flawed, create a new synthesis. Output ONLY the final chosen/synthesized step-by-step solution draft.""",
            contexts_list=hypotheses
        )

        # === PHASE 5: DRAFT CALCULATION ===
        calculation_draft = await self.generate(
            instruction=f"""Convert the synthesized hypothesis into a precise, executable calculation sequence.
            Requirements:
            - Use actual numbers from the problem
            - Show intermediate results after each step
            - Track units at every step (e.g., 35 ঘণ্টা/সপ্তাহ × 20 টাকা/ঘণ্টা = 700 টাকা/সপ্তাহ)
            - Final step must isolate the answer
            - If any step is ambiguous, state assumption explicitly
            Format: 
            Step 1: [description] → [calculation] = [result with units]
            Step 2: ...
            Final Answer: [number] [unit]""",
            context=synthesized_hypothesis
        )

        # === PHASE 6: VALIDATION & REVISION LOOP (Max 2 iterations) ===
        current_solution = calculation_draft
        for iteration in range(2):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this solution draft:
                {current_solution}

                Check for:
                1. Unit consistency at every step (e.g., ঘণ্টা × টাকা/ঘণ্টা = টাকা)
                2. Arithmetic accuracy (recalculate each step)
                3. Semantic alignment (does step match problem's intent?)
                4. Boundary conditions (no negative people, fractional items unless allowed)
                5. Final answer format (must be single number, no text)
                If any error, describe EXACTLY what and where. If perfect, say 'VALIDATED'.""",
                context=current_solution
            )

            if "VALIDATED" in validation_feedback or "validat" in validation_feedback.lower():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution based on this feedback:
                    {validation_feedback}

                    Requirements:
                    - Fix all identified errors
                    - Preserve step-by-step structure
                    - Keep unit tracking explicit
                    - Do not introduce new assumptions without labeling them""",
                    context=current_solution
                )

        # === PHASE 7: FINAL EXTRACTION & SANITY CHECK ===
        final_answer_extract = await self.summarize(
            instruction="""From the final solution, extract ONLY the numerical answer.
            Rules:
            - Must be a single number (integer or decimal)
            - Remove all units, text, and explanations
            - If multiple numbers, pick the one that answers the original question
            - If no clear number, output 'ERROR'
            - If negative or nonsensical (e.g., 0.5 people), output 'SANITY_FAIL'
            Output format: just the number or error code.""",
            context=current_solution
        )

        # === PHASE 8: FALLBACK PATH ===
        if "ERROR" in final_answer_extract or "SANITY_FAIL" in final_answer_extract:
            final_answer_extract = await self.generate(
                instruction=f"""EMERGENCY FALLBACK: The solution failed sanity check.
                Re-approach from first principles:
                1. Ignore all prior steps
                2. Extract ONLY the numbers and explicit operations from original problem
                3. Apply simplest possible interpretation
                4. Output ONLY the final number, no text
                Original problem: {self.problem_text}""",
                context=""
            )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer_extract)
        if cleaned.count('.') <= 1 and cleaned.replace('.','').isdigit():
            return cleaned
        else:
            # Last resort: return first number found in final solution
            numbers = re.findall(r'\d+\.?\d*', current_solution)
            return numbers[0] if numbers else "0"