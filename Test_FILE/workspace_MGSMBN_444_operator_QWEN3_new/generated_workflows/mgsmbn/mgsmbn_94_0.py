# Workflow ID: mgsmbn_94_0
# Benchmark: mgsmbn
# Data Indices: [135]

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

        # STEP 1: SEMANTIC DECOMPOSITION - Extract entities, relationships, constraints
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Identify and structure:

1. KNOWN QUANTITIES: List all numbers with their contextual meaning (e.g., "5টি আম" → quantity=5, item=আম, context=current possession)
2. UNKNOWN TARGET: What is being asked? (e.g., "সেথের বয়স কত?" → target=Seth's age)
3. RELATIONSHIPS: Mathematical operations implied by verbs/adjectives (e.g., "দ্বিগুণ বড়" → multiplier=2, "সমষ্টি" → addition)
4. TEMPORAL/LOGICAL ORDER: Sequence of events or conditions (e.g., "2 বছরে" → future state after 2 years)
5. CONSTRAINTS: Implicit real-world limits (e.g., ages must be positive, items can't be fractional unless specified)

Format as JSON-like structure with clear keys. Be exhaustive.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION STRATEGIES (Diamond Pattern Fork)
        algebraic_approach = self.generate(
            instruction=f"""Using the decomposition:
{decomposition}

Solve using ALGEBRAIC MODELING:
- Define variables for unknowns
- Translate relationships into equations
- Show step-by-step algebraic manipulation
- Solve symbolically before substituting numbers
- Verify solution satisfies all constraints""",
            context=decomposition
        )

        arithmetic_approach = self.generate(
            instruction=f"""Using the decomposition:
{decomposition}

Solve using STEP-BY-STEP ARITHMETIC:
- Break problem into chronological/sequential steps
- Perform calculations in order they occur in the narrative
- Track intermediate results explicitly
- Handle unit conversions if needed
- Round only at final step""",
            context=decomposition
        )

        constraint_approach = self.generate(
            instruction=f"""Using the decomposition:
{decomposition}

Solve with CONSTRAINT-FIRST REASONING:
- Begin with real-world constraints (non-negative, integer-only, etc.)
- Use estimation or bounding to narrow solution space
- Eliminate impossible values before calculation
- Prioritize physical plausibility over pure computation""",
            context=decomposition
        )

        # Execute parallel approaches
        solutions = await asyncio.gather(
            algebraic_approach,
            arithmetic_approach,
            constraint_approach
        )

        # STEP 3: INDIVIDUAL REFINEMENT
        refined_solutions = []
        for i, solution in enumerate(solutions):
            refined = await self.revise(
                instruction=f"""CRITICALLY REVISE this solution:

1. Verify mathematical accuracy: Recalculate key steps
2. Check unit consistency: Are units preserved/converted correctly?
3. Validate against constraints: Does answer respect real-world limits?
4. Improve clarity: Make reasoning steps explicit and unambiguous
5. Flag any assumptions made

If errors found, correct them. Preserve original approach style.""",
                context=solution
            )
            refined_solutions.append(refined)

        # STEP 4: ENSEMBLE SYNTHESIS
        ensemble_result = await self.ensemble(
            instruction="""SYNTHESIZE these three solution approaches into one definitive answer:

1. Compare numerical results: Do all approaches agree?
2. Resolve conflicts: If disagreement, prioritize algebraic > arithmetic > constraint-based (unless constraint violation detected)
3. Merge strongest reasoning steps from each approach
4. Output final answer as: "FINAL_ANSWER: <number>"

If fundamental disagreement remains, generate a critique explaining why and propose resolution.""",
            contexts_list=refined_solutions
        )

        # STEP 5: META-VALIDATION LOOP (Max 2 iterations)
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""META-CRITIQUE this ensemble result:
{ensemble_result}

Check for:
- Mathematical errors in final calculation
- Unit mismatches or conversion oversights
- Violation of extracted constraints (from decomposition)
- Logical inconsistencies in reasoning
- Answer format compliance (single numerical value)

If ANY issues found, describe them specifically. If perfect, respond "VALIDATED".""",
                context=ensemble_result
            )

            if "VALIDATED" in validation or "validat" in validation.lower():
                break
            else:
                # Revise based on critique
                ensemble_result = await self.revise(
                    instruction=f"""REVISE based on this critique:
{validation}

Correct all identified issues while preserving correct elements. Maintain FINAL_ANSWER format.""",
                    context=ensemble_result
                )
        else:
            # After max iterations, force final answer extraction
            pass

        # STEP 6: FINAL ANSWER EXTRACTION & SANITIZATION
        final_answer = await self.generate(
            instruction=f"""From this final result:
{ensemble_result}

Extract ONLY the numerical answer as a single number. Remove all text, units, explanations. If answer is fractional, convert to decimal. If multiple numbers present, select the one that answers the original question.

Examples:
- "FINAL_ANSWER: 16" → "16"
- "উত্তর: ১৬.৫ বছর" → "16.5"
- "x=8, so Seth is 16" → "16"

Output ONLY the number.""",
            context=ensemble_result
        )

        # Sanitize output (remove any remaining text)
        sanitized = re.sub(r'[^\d\.]', '', final_answer.strip())
        if '.' in sanitized:
            # Convert to float then back to string to normalize
            try:
                num = float(sanitized)
                if num.is_integer():
                    return str(int(num))
                return str(num)
            except:
                return sanitized
        else:
            return sanitized