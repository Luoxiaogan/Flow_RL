# Workflow ID: mgsmbn_14_0
# Benchmark: mgsmbn
# Data Indices: [154]

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

        # PHASE 1: STRUCTURAL DECOMPOSITION
        # Extract entities, quantities, relationships, and constraints with explicit unit and timing tracking
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of the Bengali math problem. Identify:
1. ALL named entities (people, objects, places) and their roles
2. ALL numerical values with units (convert Bengali digits to Arabic numerals) and what they quantify
3. Temporal sequence: what happens in what order (yearly, monthly, after, before, etc.)
4. Mathematical relationships: ratios, percentages, fractions — explicitly state base/denominator for each
5. Target unknown: what is being asked for
6. Constraints: physical (no negative items), logical (integer people), or contextual
7. Hidden steps: calculations implied but not stated
Format as structured JSON-like outline with clear section headers. Preserve Bengali terms but annotate with English equivalents in parentheses.""",
            context=""
        )

        # Compress decomposition into problem DNA for efficient context passing
        problem_dna = await self.summarize(
            instruction="""Condense the decomposition into a 5-line 'problem DNA':
Line 1: Main entities and their initial states
Line 2: Key operations and their sequence
Line 3: Critical constraints and units
Line 4: Target variable and expected format
Line 5: Potential pitfalls (e.g., percentage base, hidden steps)
Keep it ultra-concise but lossless for mathematical reconstruction.""",
            context=decomposition
        )

        # PHASE 2: PARALLEL SOLUTION PERSPECTIVES (DIAMOND FORK)
        # Generate three independent solution approaches simultaneously
        chronological_approach = self.generate(
            instruction=f"""Solve using STRICT chronological simulation:
- Start from initial state
- For each time period (year, month, etc.), apply changes step by step
- Track running totals after each operation
- Apply percentage/ratio operations ONLY to explicitly stated bases at correct timing
- Show all intermediate values with units
- Final answer must be unitless number
Problem DNA: {problem_dna}""",
            context=decomposition
        )

        algebraic_approach = self.generate(
            instruction=f"""Solve using algebraic modeling:
- Define variables for unknowns
- Write equations representing relationships
- Solve symbolically first, then substitute numbers
- Explicitly state assumptions (e.g., linear growth, constant rate)
- Verify solution satisfies all constraints
- Final answer must be unitless number
Problem DNA: {problem_dna}""",
            context=decomposition
        )

        unit_propagation_approach = self.generate(
            instruction=f"""Solve using dimensional analysis and unit propagation:
- Treat all quantities with units as physical dimensions
- Cancel units at each step to verify operation validity
- Only combine quantities with compatible units
- Track unit transformations (e.g., trees/year * years = trees)
- Final answer must emerge with correct dimension (unitless number)
Problem DNA: {problem_dna}""",
            context=decomposition
        )

        # Execute parallel approaches
        chrono_result, algebra_result, unit_result = await asyncio.gather(
            chronological_approach,
            algebraic_approach,
            unit_propagation_approach
        )

        # PHASE 3: ENSEMBLE SYNTHESIS WITH DISCREPANCY RESOLUTION
        final_answer = await self.ensemble(
            instruction="""Synthesize the three solution approaches:
1. Extract the numerical answer from each (ignore text, find number)
2. If all three agree, return that number
3. If two agree, return the majority number
4. If all differ:
   a. Check which derivation has the fewest assumptions
   b. Prefer chronological if timing is explicit in problem
   c. Prefer algebraic if relationships are proportional
   d. Prefer unit-propagation if unit consistency is critical
5. If still uncertain, default to chronological approach
Return ONLY the final numerical answer as a string (e.g., "91")""",
            contexts_list=[chrono_result, algebra_result, unit_result]
        )

        # PHASE 4: ITERATIVE VERIFICATION LOOP (MAX 2 CYCLES)
        verified_answer = final_answer
        for verification_round in range(2):
            verification = await self.revise(
                instruction=f"""STRESS TEST YOUR ANSWER:
Assume "{verified_answer}" is WRONG. Systematically check:
1. Unit mismatch? (e.g., applied percentage to wrong base)
2. Order of operations error? (e.g., added before multiplying)
3. Misread quantity? (e.g., confused initial vs final value)
4. Ignored constraint? (e.g., fractional people, negative items)
5. Timing error? (e.g., applied operation too early/late)
Recalculate ONLY the suspected faulty step. If no error found, respond exactly: "VERIFIED". Otherwise, provide corrected number.""",
                context=f"Original approaches: {chrono_result} | {algebra_result} | {unit_result}\nCurrent answer: {verified_answer}"
            )
            
            if "VERIFIED" in verification.upper():
                break
            else:
                # Extract number from verification response
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', verification)
                if numbers:
                    verified_answer = numbers[0]

        return verified_answer