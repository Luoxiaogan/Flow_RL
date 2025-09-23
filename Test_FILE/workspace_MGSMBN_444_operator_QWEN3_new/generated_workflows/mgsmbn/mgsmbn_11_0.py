# Workflow ID: mgsmbn_11_0
# Benchmark: mgsmbn
# Data Indices: [143, 118]

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

        # STEP 1: SEMANTIC DECOMPOSITION — Extract problem structure
        problem_schema = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Identify and structure:

1. ENTITIES: List all actors/objects (e.g., 'Chinese team', 'John', 'pineapples').
2. QUANTITIES: Extract all numbers and what they represent (e.g., '240 Asians', '100 pineapples/hectare').
3. RELATIONSHIPS: Describe how entities and quantities relate (e.g., '80 are Japanese, rest are Chinese').
4. TARGET: What is the question asking for? Be explicit.
5. CONSTRAINTS: Any implicit rules (e.g., 'people can't be fractional', 'harvests occur every 3 months').

Format as a structured JSON-like outline. Be exhaustive. This will guide all subsequent reasoning.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION — Explore 4 solution archetypes
        strategy_instructions = [
            """You are a SEQUENTIAL ARITHMETIC expert. Solve the problem by identifying step-by-step calculations in chronological or logical order. 
            - Start from given values.
            - Apply additions, subtractions, multiplications, divisions in correct sequence.
            - Show intermediate results.
            - Example: "Total Chinese = 240 - 80 = 160. Girls = 160 - 60 = 100."
            Use the problem schema to ground your steps.""",
            
            """You are a RATE & CYCLE expert. Focus on problems involving time, repetition, or scaling.
            - Identify rate per unit (e.g., per hour, per hectare, per month).
            - Identify number of cycles or intervals (e.g., 4 times a year if every 3 months).
            - Compute total = rate × cycles × base quantity.
            - Example: "100 pineapples/hectare × 10 hectares × 4 harvests = 4000."
            Use the problem schema to identify rates and cycles.""",
            
            """You are a PROPORTION & DISTRIBUTION expert. Solve by ratios, fractions, or allocations.
            - Identify total quantity and how it's partitioned.
            - Compute shares using subtraction or division.
            - Handle remainders or subgroup splits.
            - Example: "Chinese = 240 - 80 = 160. Girls = 160 - 60 = 100."
            Use the problem schema to identify partitions and subgroups.""",
            
            """You are an ALGEBRAIC REASONING expert. Assign variables to unknowns and solve equations.
            - Define variable for the target quantity.
            - Write equation based on relationships.
            - Solve step-by-step.
            - Example: "Let G = girls. 80 + 60 + G = 240 → G = 100."
            Use the problem schema to define variables and relationships."""
        ]

        # Generate strategies in parallel
        raw_strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_schema) for instr in strategy_instructions]
        )

        # STEP 3: VALIDATE & REFINE EACH STRATEGY
        refined_strategies = []
        for i, strategy in enumerate(raw_strategies):
            refined = await self.revise(
                instruction=f"""Critically validate and refine this solution strategy (Strategy {i+1}). Check:

1. ARITHMETIC: Are all calculations correct? Recompute if needed.
2. UNITS: Are units tracked and consistent? (e.g., টাকা, ঘণ্টা, জিনিস)
3. LOGIC: Does the sequence make sense? Are hidden steps uncovered?
4. CONTEXT: Is the answer plausible? (e.g., no negative people, fractional boxes only if allowed)

If any flaw is found, correct it explicitly. Show your validation steps. Preserve the original strategy’s core approach but make it rigorous.""",
                context=strategy
            )
            refined_strategies.append(refined)

        # STEP 4: ENSEMBLE SYNTHESIS — Merge or select best
        final_answer_draft = await self.ensemble(
            instruction="""You are the final arbiter. Synthesize the solutions below:

1. Compare all refined strategies. Do they agree numerically?
2. If YES: Output the consensus number.
3. If NO: Analyze why. Which solution:
   - Respects all constraints from the problem schema?
   - Has the clearest, most complete step-by-step justification?
   - Tracks units and intermediate values correctly?
4. Select or merge the best solution. If ambiguity remains, prefer the solution that explicitly states assumptions.
5. Output ONLY the final numerical answer in this format: "ANSWER: <number>" — nothing else.""",
            contexts_list=refined_strategies
        )

        # STEP 5: FINAL EXTRACTION — Ensure pure numerical output
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below. 

Rules:
- Remove all units, explanations, or qualifiers.
- If multiple numbers exist, select the one that directly answers the original question.
- If no clear number, return "0" as fallback.
- Output must be a single integer or decimal number. Nothing else.

Example: If input is "ANSWER: 100", output "100". If input is "The result is 4000 pineapples", output "4000".""",
            context=final_answer_draft
        )

        # Clean and return
        # Strip non-numeric except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        return cleaned if cleaned else "0"