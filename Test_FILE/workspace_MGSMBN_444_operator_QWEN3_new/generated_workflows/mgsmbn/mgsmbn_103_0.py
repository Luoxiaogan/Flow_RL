# Workflow ID: mgsmbn_103_0
# Benchmark: mgsmbn
# Data Indices: [86]

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

        # === PHASE 1: LINGUISTIC DECONSTRUCTION & ENTITY MAPPING ===
        entity_map = await self.generate(
            instruction="""Perform a deep semantic decomposition of the Bengali word problem. Extract and structure the following:

1. ENTITIES: List all actors (people, organizations), objects (items, containers), and locations. For each, note their role.
2. QUANTITIES: Extract every number mentioned. For each, specify:
   - The value
   - The unit (টাকা, গ্যালন, ঘণ্টা, জিনিস, etc.)
   - What it describes (e.g., "price per gallon", "total time")
   - Whether it's given or unknown
3. EVENTS & RELATIONSHIPS: Chronological or causal sequence of actions. Map which quantities are affected by which events.
4. CONSTRAINTS: Explicit limits (e.g., "no more than 10") and implicit ones (e.g., "can't have negative money", "whole people only").
5. GOAL: Precisely restate what is being asked. Identify the target variable.

Format output as clearly labeled sections. Be exhaustive. Preserve Bengali terms where meaning is culturally specific.""",
            context=""
        )

        # Revise for completeness and consistency
        verified_entity_map = await self.revise(
            instruction="""Critically review the entity map. Check for:

- Missing numbers or misassigned units
- Unclear references (e.g., 'he' without antecedent)
- Unresolved pronouns or ambiguous quantities
- Contradictions between events and quantities
- Units that don't propagate correctly to the goal

Fill gaps using conservative assumptions. Flag any remaining ambiguities explicitly. Ensure every number in the original problem is accounted for.""",
            context=entity_map
        )

        # === PHASE 2: PARALLEL STRATEGY GENERATION ===
        procedural_attempt, equation_attempt, unit_analysis_attempt = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using STEP-BY-STEP PROCEDURAL REASONING:

Guidelines:
- Follow the chronological order of events as described.
- For each sentence or clause, translate into an arithmetic operation.
- Track intermediate results WITH UNITS at every step.
- Never combine steps. Show explicit calculations.
- Validate that each step's output makes real-world sense (no negative items, etc.).
- Final answer must directly answer the goal stated in the entity map.

Entity context for reference:
{verified_entity_map}""",
                context=verified_entity_map
            ),
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:

Guidelines:
- Define variables for unknowns (use descriptive names).
- Translate relationships into equations or inequalities.
- Solve symbolically first, then substitute numbers.
- Show all algebraic manipulations.
- Verify solution satisfies original conditions and constraints.
- Final answer must be numerical and match the goal.

Entity context for reference:
{verified_entity_map}""",
                context=verified_entity_map
            ),
            self.generate(
                instruction=f"""Solve using DIMENSIONAL ANALYSIS & UNIT PROPAGATION:

Guidelines:
- Ignore numerical values initially. Focus ONLY on units.
- Map how units transform through operations (e.g., টাকা/গ্যালন × গ্যালন → টাকা).
- Identify the unit of the final answer. Work backward to required operations.
- Only then plug in numbers, ensuring unit consistency at each step.
- Flag any unit mismatch or undefined operation.
- Final answer must have correct unit (then remove unit for output).

Entity context for reference:
{verified_entity_map}""",
                context=verified_entity_map
            )
        )

        # === PHASE 3: ENSEMBLE SYNTHESIS WITH CONFLICT DIAGNOSIS ===
        first_ensemble_result = await self.ensemble(
            instruction="""You are given three solution attempts for the same Bengali math problem. Your task:

1. COMPARE: Identify where they agree and where they diverge.
2. DIAGNOSE: For each divergent answer, explain WHY it likely failed:
   - Procedural: Missed step? Wrong order? Ignored event?
   - Algebraic: Incorrect equation? Misdefined variable?
   - Unit-based: Unit mismatch? Invalid operation?
3. SELECT: Choose the most logically consistent answer. Prioritize:
   - Unit consistency
   - Constraint satisfaction
   - Chronological/event fidelity
4. If all three disagree significantly, reconstruct from entity map using conservative assumptions.
5. Output ONLY the final numerical answer, but internally note confidence level.

DO NOT average or blend. Choose the best-supported answer.""",
            contexts_list=[procedural_attempt, equation_attempt, unit_analysis_attempt]
        )

        # === PHASE 4: ITERATIVE SELF-CRITIQUE (MAX 2 ITERATIONS) ===
        current_answer = first_ensemble_result
        for iteration in range(2):
            critique = await self.revise(
                instruction=f"""Adversarial Self-Critique:

Assume the following answer is WRONG. Attack it mercilessly:

Current Answer: {current_answer}

Check for:
1. MISREAD QUANTITIES: Did we extract the wrong number or unit from the problem?
2. OPERATION ORDER: Did we apply operations in incorrect sequence (e.g., added before multiplying)?
3. UNIT ERRORS: Did units not cancel or convert properly?
4. CONSTRAINT VIOLATIONS: Does answer imply fractional people, negative money, or impossible quantities?
5. LOGICAL GAPS: Did we skip an implied step (e.g., tax applied after discount)?

If you find a fatal flaw, propose a CORRECTED numerical answer. If no flaw, return the same answer.""",
                context=current_answer
            )

            # If critique proposes a different answer, re-ensemble to decide
            if critique.strip() != current_answer.strip():
                adjudication = await self.ensemble(
                    instruction=f"""Compare two answers for the same problem:

Original: {current_answer}
Critique Proposal: {critique}

Which is more defensible? Consider:
- Which better respects the entity map and constraints?
- Which has fewer logical leaps?
- Which maintains unit consistency?

Choose one. Output ONLY the chosen numerical answer.""",
                    contexts_list=[current_answer, critique]
                )
                current_answer = adjudication
            else:
                # No change, exit loop early
                break

        # === FINAL OUTPUT SANITIZATION ===
        final_answer_clean = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below. It must be:

- A single number (integer or decimal)
- No units, no text, no explanations
- If multiple numbers appear, choose the one that directly answers the problem's goal

If the input is already a clean number, return it unchanged.""",
            context=current_answer
        )

        # Strip any remaining non-numeric characters (safety net)
        sanitized = re.sub(r'[^\d.-]', '', final_answer_clean.strip())
        # Handle edge case where multiple numbers might remain
        numbers = re.findall(r'-?\d+\.?\d*', sanitized)
        if numbers:
            return numbers[0]  # Return first number as fallback
        else:
            return "0"  # Ultimate fallback (should never trigger)