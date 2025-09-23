# Workflow ID: mgsmbn_3_0
# Benchmark: mgsmbn
# Data Indices: [39]

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

        # PHASE 1: META-COGNITIVE TRIAGE — Classify problem structure and requirements
        classification = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math word problem. Do NOT solve it yet. Instead, output a structured classification with these sections:

1. PROBLEM TYPE: Identify primary category (Rate, Distribution, Comparison, Multi-entity, Proportional, Sequential, Other) and secondary tags.
2. ENTITIES & QUANTITIES: List all named entities (people, objects) with their associated quantities and units. Include implicit quantities.
3. RELATIONSHIPS & ACTIONS: Describe mathematical relationships (ratios, sums, differences) and chronological actions.
4. TARGET UNKNOWN: Explicitly state what numerical value is being asked for.
5. POTENTIAL PITFALLS: List likely misinterpretations, unit conversion needs, or hidden constraints.
6. STRATEGIC APPROACH: Recommend 2-3 viable solution strategies ranked by suitability.

Format each section clearly with headers. Be exhaustive — this classification will drive all subsequent reasoning.""",
            context=""
        )

        # PHASE 2: STRUCTURED CONTEXT BUILDING — Summarize classification into focused schema
        problem_schema = await self.summarize(
            instruction="""Condense the classification into a minimal, structured schema for downstream solvers. Format exactly as:

Entities: {concise list with quantities}
Target: {what to solve for}
Constraints: {key limitations or conditions}
Recommended Strategies: {top 2 strategies}

Remove all explanatory text — only structured data. This will be the working context for solution generation.""",
            context=classification
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION — Three independent approaches
        algebraic_approach, procedural_approach, dimensional_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
- Define variables for unknowns
- Write equations based on relationships in schema: {problem_schema}
- Solve step-by-step with substitution/elimination
- Track units at every step
- Box final answer as \\boxed{{value}}
Context: {problem_schema}""",
                context=problem_schema
            ),
            self.generate(
                instruction=f"""Solve using STEP-BY-STEP PROCEDURAL REASONING:
- Start from initial state described in schema: {problem_schema}
- Apply each action chronologically
- Show intermediate results after each operation
- Verify unit consistency at each step
- Box final answer as \\boxed{{value}}
Context: {problem_schema}""",
                context=problem_schema
            ),
            self.generate(
                instruction=f"""Solve using DIMENSIONAL ANALYSIS / UNIT TRACKING:
- Identify all units and conversion factors needed (schema: {problem_schema})
- Set up calculation as unit cancellation chain
- Show dimensional analysis at each step
- Verify final unit matches target
- Box final answer as \\boxed{{value}}
Context: {problem_schema}""",
                context=problem_schema
            )
        )

        # PHASE 4: ENSEMBLE SYNTHESIS — Weighted consensus with error detection
        ensemble_result = await self.ensemble(
            instruction="""Synthesize the three solution attempts into one optimal answer. Evaluate each on:
1. MATHEMATICAL CORRECTNESS: Are operations and logic sound?
2. UNIT HANDLING: Are units tracked and converted properly?
3. CONTEXTUAL PL AUSIBILITY: Does answer make sense in real-world context?
4. STEP CLARITY: Are intermediate steps explicit and verifiable?

Select the strongest solution, but feel free to hybridize — take correct arithmetic from one, unit handling from another, etc. If all solutions agree, output that answer. If they conflict, perform majority vote with quality weighting. Final output must be a single solution with clear steps and boxed answer.""",
            contexts_list=[algebraic_approach, procedural_approach, dimensional_approach]
        )

        # PHASE 5: ADVERSARIAL VERIFICATION — Actively try to break the solution
        verified_solution = await self.revise(
            instruction=f"""Play DEVIL'S ADVOCATE to stress-test this solution:
1. Check for unit mismatches or unconverted units
2. Verify no negative quantities where impossible (people, time, etc.)
3. Confirm chronological logic (e.g., can't spend money before earning)
4. Validate division doesn't use zero denominator
5. Ensure fractional answers are appropriate (e.g., no 0.5 people unless context allows)
6. Re-calculate key steps independently

If ANY issues found, revise solution completely — don't just patch. If no issues, return solution unchanged. Maintain boxed answer format.""",
            context=ensemble_result
        )

        # PHASE 6: FINAL EXTRACTION — Pull numerical answer from verified solution
        # Use regex to find boxed answer or last numerical value
        final_answer_match = re.search(r'\\boxed\{([0-9.,]+)\}', verified_solution)
        if not final_answer_match:
            # Fallback: find last number in text
            numbers = re.findall(r'[0-9]+\.?[0-9]*', verified_solution)
            final_answer = numbers[-1] if numbers else "0"
        else:
            final_answer = final_answer_match.group(1)

        # Return as string (will be converted to number by evaluator)
        return final_answer