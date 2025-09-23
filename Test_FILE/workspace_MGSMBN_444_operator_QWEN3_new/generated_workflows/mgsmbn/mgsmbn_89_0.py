# Workflow ID: mgsmbn_89_0
# Benchmark: mgsmbn
# Data Indices: [90, 66]

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
        import json

        # === STAGE 1: META-CLASSIFICATION & SEMANTIC EXTRACTION ===
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this Bengali math problem. Identify:
1. Problem type: Classify as one or more of [Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity]
2. Key entities: Extract all named objects/people with their quantities (e.g., "2টি ফুল" → flower: 2)
3. Temporal markers: Note time spans, sequences, or conditions (e.g., "15 দিন পরে", "যদি...তবে")
4. Mathematical operations implied: Map verbs/phrases to operations (e.g., "লাগিয়েছেন" → addition, "না বেড়ে ওঠে" → subtraction)
5. Constraints: Note real-world limits (non-negative, integer-only, unit consistency)
6. Target: What is being asked? (e.g., "মোট কটি" → total count, "কত বেশি" → difference)
Output as structured JSON with keys: problem_type, entities, time_markers, operations, constraints, target.""",
            context=""
        )

        # === STAGE 2: PARALLEL STRATEGY GENERATION ===
        # Generate 3 solution approaches based on problem type
        strategy_instructions = [
            """Using ALGEBRAIC approach: Define variables for unknowns, set up equations based on relationships in the problem, solve systematically. Show all steps. Assume linear relationships unless specified otherwise.""",
            """Using ARITHMETIC SEQUENTIAL approach: Solve step-by-step in chronological order. Track state changes (e.g., initial → after event 1 → after event 2). Explicitly show intermediate values.""",
            """Using PROPORTIONAL/UNITARY approach: Identify rates, ratios, or per-unit values. Scale up/down based on given multipliers. Use cross-multiplication where applicable."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}

Context from problem analysis:
{problem_analysis}

IMPORTANT: 
- Maintain unit consistency throughout
- Verify intermediate results make real-world sense
- If fractional results occur, check constraints from analysis before finalizing
- Output final answer as a single number with brief justification""",
                context=problem_analysis
            ) for instr in strategy_instructions]
        )

        # === STAGE 3: CONSTRAINT-AWARE REVISION ===
        revised_attempts = []
        for attempt in strategy_attempts:
            revised = await self.revise(
                instruction=f"""Critically revise this solution attempt:

1. UNIT CHECK: Are all units consistent? (e.g., টাকা, ঘণ্টা, জিনিস)
2. INTEGER CONSTRAINT: If problem involves countable objects/people, is answer integer? If not, apply floor/ceil/remainder based on context.
3. NON-NEGATIVE: Does answer make sense in real world? (no negative flowers, people, etc.)
4. STEP VALIDATION: Verify each calculation step. Recompute if arithmetic error suspected.
5. CONTEXT ALIGNMENT: Does final answer match what was asked? (e.g., if asked for difference, not total)

If any issue found, FIX it and explain correction. If no issues, output "VALID: [original answer]".""",
                context=attempt
            )
            revised_attempts.append(revised)

        # === STAGE 4: ENSEMBLE SYNTHESIS WITH CONFIDENCE CHECK ===
        final_answer = await self.ensemble(
            instruction="""Synthesize the three revised solution attempts into final answer:

1. If all 3 agree numerically → return that number immediately
2. If 2 agree and 1 differs → return majority answer with note
3. If all differ → identify most logically consistent solution based on:
   - Adherence to extracted constraints
   - Step-by-step validity
   - Alignment with problem semantics
   - Mathematical rigor

OUTPUT FORMAT: Single numerical value only (integer or decimal). No units, no explanation.""",
            contexts_list=revised_attempts
        )

        # === STAGE 5: FINAL VALIDATION & EXTRACTION ===
        # Extract just the number from ensemble output (handles cases where it includes text)
        clean_answer = await self.generate(
            instruction="""Extract ONLY the numerical answer from the following text. 
If multiple numbers present, choose the one that is final answer. 
If no clear number, return 0.

OUTPUT: Single number only. No words, no units, no punctuation.""",
            context=final_answer
        )

        return clean_answer.strip()