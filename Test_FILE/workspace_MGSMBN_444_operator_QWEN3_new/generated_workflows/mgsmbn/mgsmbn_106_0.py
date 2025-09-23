# Workflow ID: mgsmbn_106_0
# Benchmark: mgsmbn
# Data Indices: [131]

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
            instruction="""Perform deep semantic parsing of the Bengali math problem. Extract and structure ALL quantifiable elements in this exact format:

Entities:
- People: [list names and their associated quantities/actions]
- Objects: [list items being counted/measured with units]
- Actions: [verbs indicating mathematical operations: add, subtract, multiply, divide, compare]
- Quantities: [all numbers with their referents and units]
- Goal: [what the problem asks to find]

Constraints:
- Explicit: [stated limitations or conditions]
- Implicit: [real-world assumptions: e.g., no negative fish, whole people]

Relationships:
- [Entity A] [relation] [Entity B] (e.g., "Loksin caught 5 less than Anakin")

Output ONLY in this structured format. Be exhaustive.""",
            context=""
        )

        # STEP 2: CLEAN & FOCUS THE EXTRACTION (REMOVE NARRATIVE FLUFF)
        cleaned_extraction = await self.revise(
            instruction="""Revise the extracted structure to:
1. Remove all decorative narrative (times, locations, emotions unless quantified)
2. Standardize unit notation (e.g., 'টাকা' → 'TK', 'ঘণ্টা' → 'hr')
3. Annotate each quantity with its mathematical role (base value, delta, rate, total)
4. Flag any ambiguous references that need disambiguation
5. Ensure all relationships are mathematically explicit (convert "5 less" to "-5")

Output the cleaned, mathematically-ready structure.""",
            context=extraction
        )

        # STEP 3: PROBLEM TYPE CLASSIFICATION (CONDITIONAL BRANCHING)
        classification = await self.generate(
            instruction=f"""Classify this problem into ONE primary type with confidence score (0-100%):

1. Sequential Operations (multiple steps in time/order)
2. Rate Problems (speed, work rate, unit price)
3. Proportional Reasoning (ratios, percentages, scaling)
4. Distribution (division, sharing, remainders)
5. Comparison (differences, "how many more")
6. Multi-entity Tracking (multiple actors with different quantities)

Also identify:
- Required operations (add, subtract, multiply, divide, algebra)
- Hidden steps needed (intermediate calculations not stated)
- Unit conversion requirements

Format:
Type: [type] (Confidence: X%)
Operations: [list]
Hidden Steps: [list or "None"]
Unit Conversions: [list or "None"]""",
            context=cleaned_extraction
        )

        # STEP 4: PARALLEL SOLUTION GENERATION (DIAMOND PATTERN)
        # Generate 3 solution approaches based on classification
        solution_approaches = [
            """Solve using direct arithmetic: compute each entity's total separately then combine. Show all steps.""",
            """Solve using algebraic modeling: define variables for unknowns, set up equations, solve systematically.""",
            """Solve using proportional reasoning: identify ratios or scaling factors first, then apply to totals."""
        ]

        # Dynamically tailor instructions based on classification
        tailored_instructions = []
        for approach in solution_approaches:
            tailored_instructions.append(
                f"""Given problem classification: {classification}

{approach}

Additional constraints from extraction: {cleaned_extraction}

- Show ALL intermediate calculations
- Track units at every step
- Verify no negative/invalid quantities for discrete items
- Box final answer as: \\boxed{{number}}"""
            )

        # Generate solutions in parallel
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in tailored_instructions]
        )

        # STEP 5: ENSEMBLE - SYNTHESIZE & SELECT BEST SOLUTION
        final_solution = await self.ensemble(
            instruction="""Evaluate all solution attempts:

1. Check mathematical correctness (arithmetic, operations)
2. Verify unit consistency throughout
3. Ensure all constraints from original problem are satisfied
4. Confirm answer format is single numerical value
5. Prefer solutions that explicitly handle hidden steps

If all solutions agree, output the consensus answer.
If they conflict, synthesize a hybrid solution using the most consistent steps from each.
Final output MUST be ONLY the numerical answer (integer or decimal) with no explanation.""",
            contexts_list=solution_attempts
        )

        # STEP 6: SANITY CHECK & REVISION (ITERATIVE LOOP)
        for _ in range(2):  # Max 2 revision cycles
            sanity_check = await self.generate(
                instruction=f"""Validate this answer against original problem:

Answer: {final_solution}
Original Context: {cleaned_extraction}

Check:
1. Does this answer make real-world sense? (e.g., no fractional people if context implies whole entities)
2. Are all quantities non-negative where required?
3. Does it satisfy the problem's explicit question?
4. Are units consistent?

If valid, output "VALID: [answer]".
If invalid, output "INVALID: [specific reason]".""",
                context=final_solution
            )

            if "INVALID" in sanity_check:
                final_solution = await self.revise(
                    instruction=f"""Revise the solution based on this validation error:

{sanity_check}

Original problem context: {cleaned_extraction}
Previous solution: {final_solution}

Generate corrected solution with proper handling of the error.
Output ONLY the numerical answer.""",
                    context=final_solution
                )
            else:
                break

        # STEP 7: FINAL EXTRACTION (ENSURE NUMERIC OUTPUT)
        # Extract just the number from the final solution (handles \boxed{} or other formatting)
        numeric_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from this text. 
If multiple numbers exist, select the one that answers the original question.
If no clear number, output 0.

Output format: single number (integer or decimal) with no units or text.""",
            context=final_solution
        )

        return numeric_answer.strip()