# Workflow ID: mgsmbn_34_0
# Benchmark: mgsmbn
# Data Indices: [162]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for MGSM Bengali: adaptive, validated, multi-strategy.
        """
        import asyncio
        import re

        # === STEP 1: SEMANTIC EXTRACTION & CLASSIFICATION ===
        extraction = await self.generate(
            instruction="""You are a Bengali math problem analyzer. Your task is to extract and structure ALL mathematical components from the problem text.

            Follow this exact format:

            ENTITIES:
            - [Entity Name]: [Description and role]

            NUMBERS & UNITS:
            - [Number] [Unit]: [What it represents, semantic role: RATE, TOTAL, QUANTITY, DURATION, etc.]

            RELATIONSHIPS:
            - [Relationship description, e.g., "5 tons per acre", "2 barrels per ton"]

            PROBLEM TYPE CLASSIFICATION:
            - Primary Type: [Rate, Distribution, Comparison, Sequential, Proportional, Multi-entity]
            - Secondary Tags: [Unit Conversion, Remainder, Fraction, Percentage, etc.]

            CONSTRAINTS:
            - [Any implicit or explicit constraints: e.g., "non-negative", "integer only", "must be divisible"]

            UNKNOWN:
            - [What we are solving for, with expected unit]

            Be exhaustive. Do not solve yet. Just extract and classify.
            """,
            context=""
        )

        # === STEP 2: PARALLEL STRATEGY GENERATION ===
        strategy_instructions = [
            """You are a direct calculation strategist. Given the extracted structure, propose the SHORTEST possible mathematical path to the answer.
            - Use direct formulas if possible.
            - Show minimal steps.
            - Assume unit consistency unless flagged.
            - Output ONLY the calculation steps and final expression.""",
            
            """You are a step-by-step decomposition strategist. Break the problem into atomic subproblems.
            - Solve each subproblem independently.
            - Show intermediate results with units.
            - Combine at the end.
            - Annotate each step with its purpose.""",
            
            """You are a unit-first conversion strategist. Start from the target unit and work backward.
            - Map all given units to the target unit.
            - Show conversion factors explicitly.
            - Validate dimensional consistency at each step.
            - Highlight any unit assumptions made."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=extraction) for instr in strategy_instructions]
        )

        # === STEP 3: ENSEMBLE BEST STRATEGY ===
        selected_strategy = await self.ensemble(
            instruction="""You are a strategy selector. Given three solution approaches, choose the MOST RELIABLE and COMPLETE one.

            Criteria:
            1. Correctly handles units and conversions.
            2. Matches the problem type classification.
            3. Accounts for all constraints.
            4. Has clear, traceable steps.
            5. Minimizes ambiguity.

            If none are perfect, SYNTHESIZE a hybrid approach by combining the best elements.

            Output the final chosen strategy in clear, numbered steps.""",
            contexts_list=strategy_attempts
        )

        # === STEP 4: EXECUTE & VALIDATE ===
        raw_solution = await self.generate(
            instruction=f"""Execute the chosen strategy step by step. Show ALL work.

            Strategy to follow:
            {selected_strategy}

            Requirements:
            - Write each calculation explicitly.
            - Track units at every step.
            - Box the final numerical answer at the end.
            - If any step seems ambiguous, state your assumption clearly.
            """,
            context=selected_strategy
        )

        # === STEP 5: SANITY & UNIT VALIDATION ===
        validated_solution = await self.revise(
            instruction="""You are a validation expert. Critique this solution:

            1. UNIT CHECK: Are units consistent throughout? Are final units correct?
            2. SANITY CHECK: Is the answer plausible? (e.g., no negative people, no fractional children)
            3. CONSTRAINT CHECK: Does it respect all extracted constraints?
            4. ARITHMETIC CHECK: Verify one critical calculation manually.

            If any issue is found, REVISE the solution to fix it. Otherwise, return it unchanged.

            Preserve the final boxed answer format.
            """,
            context=raw_solution
        )

        # === STEP 6: FINAL ANSWER EXTRACTION ===
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.

            Rules:
            - It must be a single number (integer or decimal).
            - Remove all units, text, and explanations.
            - If multiple numbers exist, pick the one in the final boxed expression.
            - If no clear answer, return "0" as fallback.

            Example outputs: "100", "25.5", "0"
            """,
            context=validated_solution
        )

        # Clean and return
        # Strip non-numeric except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        if cleaned.count('.') > 1:
            cleaned = cleaned.split('.')[0] + '.' + ''.join(cleaned.split('.')[1:])

        return cleaned if cleaned else "0"