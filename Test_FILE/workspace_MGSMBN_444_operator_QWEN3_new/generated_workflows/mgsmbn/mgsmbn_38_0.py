# Workflow ID: mgsmbn_38_0
# Benchmark: mgsmbn
# Data Indices: [87]

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

        # STEP 1: Deep Entity and Relationship Extraction
        entity_extraction = await self.generate(
            instruction="""Thoroughly deconstruct the Bengali word problem into structured mathematical components. Identify and categorize:

1. NUMERICAL ENTITIES: All numbers with their contextual meaning (e.g., "24 রোল-আপ লম্বা" → length=24 units)
2. ACTORS: People/objects involved and their associated quantities
3. OPERATIONS: Explicit or implicit mathematical operations (addition, multiplication, averaging, etc.)
4. UNITS & DIMENSIONS: Physical or abstract units (টাকা, ঘণ্টা, রোল-আপ) and their relationships
5. CONSTRAINTS: Real-world limitations (non-negative, integer-only, temporal order)
6. TARGET: What is being asked for? What form should the answer take?

Format as JSON-like structure with clear labels. Preserve Bengali terms where meaning is context-dependent.""",
            context=""
        )

        # STEP 2: Parallel Strategy Generation (Literal, Algebraic, Spatial)
        strategy_instructions = [
            """Solve using LITERAL STEP-BY-STEP ARITHMETIC:
- Break problem into chronological or logical sequence of operations
- Perform calculations in order they appear in narrative
- Show intermediate results with units
- Handle unit conversions explicitly
- Final output must be single numerical value""",
            
            """Solve using ALGEBRAIC MODELING:
- Define variables for unknowns and knowns
- Set up equations based on relationships described
- Solve system of equations step by step
- Substitute values only at end to minimize rounding errors
- Verify solution satisfies all constraints""",
            
            """Solve using SPATIAL/VISUAL REASONING:
- Interpret quantities as geometric or discrete units (areas, grids, groups)
- Model problem visually (e.g., roll-ups as rectangles, items as arrays)
- Compute totals through multiplication/division of dimensions
- Consider discrete vs continuous interpretations
- Round only if context demands whole units"""
        ]

        strategy_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=entity_extraction) for instr in strategy_instructions]
        )

        # STEP 3: Adversarial Critique Loop (Two Rounds)
        revised_solutions = []
        for i, solution in enumerate(strategy_solutions):
            # First revision: Internal consistency check
            critique_v1 = await self.generate(
                instruction=f"""CRITIQUE THIS SOLUTION ADVERSARIALLY:
Assume this solution contains at least one critical error. Systematically check:
1. Unit consistency: Are all operations dimensionally valid?
2. Order of operations: Does sequence match problem's logic?
3. Constraint violation: Does answer respect real-world limits (non-negative, integer if required)?
4. Arithmetic accuracy: Recompute key steps independently
5. Interpretation error: Could Bengali terms have been misread?

Output ONLY the most likely error and how to fix it.""",
                context=solution
            )
            
            revised_v1 = await self.revise(
                instruction=f"""REVISE BASED ON CRITIQUE:
Incorporate this critique: {critique_v1}
- Fix identified errors
- Add explicit unit tracking
- Show corrected calculation steps
- Preserve original strategy's core approach""",
                context=solution
            )
            
            # Second revision: Contextual plausibility
            critique_v2 = await self.generate(
                instruction="""FINAL SANITY CHECK:
Does this revised solution make sense in the real-world context?
- Would the numbers be physically possible? (e.g., can a person eat 1000 roll-ups?)
- Does the answer format match what was asked? (integer, decimal, specific unit)
- Are there cultural or linguistic nuances in Bengali that might affect interpretation?
- Is the 'average' or 'total' correctly applied?

If any issue, specify exact correction needed.""",
                context=revised_v1
            )
            
            revised_v2 = await self.revise(
                instruction=f"""FINAL REVISION:
Incorporate sanity check: {critique_v2}
- Make minimal changes to fix plausibility issues
- Ensure answer is single numerical value
- Remove all explanatory text - keep only final number and essential calculation steps""",
                context=revised_v1
            )
            revised_solutions.append(revised_v2)

        # STEP 4: Ensemble Synthesis with Constraint Anchoring
        final_answer = await self.ensemble(
            instruction="""SYNTHESIZE FINAL ANSWER THROUGH CROSS-VALIDATION:
1. Compare all three revised solutions. Where they numerically agree, accept that value.
2. Where they disagree, trace back to first principles using original problem constraints.
3. Prioritize solutions that:
   - Maintain unit consistency throughout
   - Respect real-world constraints (no fractional people, negative quantities)
   - Match the problem's explicit request (average, total, difference, etc.)
4. If still uncertain, compute simple average of solutions - but only if all are plausible.
5. OUTPUT ONLY THE FINAL NUMERICAL VALUE. No units, no explanation.

Anchor decision to extracted entities and constraints from Step 1.""",
            contexts_list=revised_solutions
        )

        # STEP 5: Recursive Narrative Validation (Max 2 iterations)
        for validation_round in range(2):
            narrative_check = await self.generate(
                instruction=f"""NARRATIVE VALIDATION:
Given answer: {final_answer}
Reconstruct the problem's story with this number. Ask:
- Does this number make sense in context? (e.g., if average is 45, do individual values seem plausible?)
- Is there any contradiction with original problem statement?
- Could rounding or unit conversion have introduced error?

If answer is inconsistent, output "RECOMPUTE" followed by correction strategy. Otherwise, output "VALID".""",
                context=entity_extraction
            )
            
            if "RECOMPUTE" in narrative_check:
                # Simple correction: adjust based on most consistent strategy
                recalc_strategy = await self.generate(
                    instruction=f"""RECOMPUTE WITH CORRECTION:
Original issue: {narrative_check}
Use the most reliable strategy (usually literal arithmetic) to recompute.
Focus on the specific step that caused inconsistency.
Output only the corrected numerical value.""",
                    context=entity_extraction
                )
                final_answer = recalc_strategy
            else:
                break  # Answer validated

        # Extract just the number from final answer (remove any residual text)
        # Look for first number in string (handles cases where operators output extra text)
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if number_match:
            return float(number_match.group()) if '.' in number_match.group() else int(number_match.group())
        else:
            # Fallback: return as string if no number found (shouldn't happen in well-formed workflow)
            return final_answer.strip()