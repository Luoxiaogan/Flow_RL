# Workflow ID: mgsmbn_28_0
# Benchmark: mgsmbn
# Data Indices: [3, 56]

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

        # STEP 1: DECOMPOSE THE PROBLEM INTO STRUCTURED COMPONENTS
        decomposition = await self.generate(
            instruction="""Thoroughly decompose this Bengali math word problem into its core components. Identify and explicitly state:

1. ENTITIES: All objects, people, or groups involved (e.g., 'chickens', 'Wendy', 'sandcastle floors'). Specify counts if given.
2. QUANTITIES: All numerical values with their associated units and what they represent (e.g., '15 cups in the morning', '16 sq ft for top floor').
3. RELATIONSHIPS: How quantities relate (e.g., 'each chicken gets 3 cups daily', 'each floor is half the area of the one below').
4. SEQUENCE: Temporal or logical order of events (e.g., 'morning → afternoon → evening feeding').
5. TARGET: The exact unknown being asked for, phrased as a complete question (e.g., 'How many cups must Wendy give in the final feeding?').
6. CONSTRAINTS: Any implicit or explicit limitations (e.g., 'must be non-negative', 'whole chickens only').

Format your response clearly with labeled sections. Be exhaustive — do not omit any detail, no matter how small. This decomposition will drive all subsequent reasoning.""",
            context=""
        )

        # STEP 2: CLASSIFY PROBLEM TYPE AND SELECT PRIMARY STRATEGY
        classification = await self.generate(
            instruction=f"""Based on this decomposition:

{decomposition}

Classify the problem type and select the most appropriate solution strategy:

- SEQUENTIAL: Events happen in order; solution requires step-by-step simulation.
- PROPORTIONAL: Involves ratios, scaling, or percentages.
- RECURSIVE/GEOMETRIC: Each step depends on previous (e.g., halving, doubling).
- DISTRIBUTION: Dividing or allocating quantities among entities.
- COMPARISON: Finding differences or relative quantities.

Also determine:
- Primary mathematical operations needed (add, multiply, etc.)
- Whether units must be tracked or converted
- Whether intermediate rounding is required
- Whether the answer must be integer or can be decimal

Finally, outline a brief solution roadmap: 'First do X, then Y, then Z to find the answer.'

Be explicit and justify your classification.""",
            context=decomposition
        )

        # STEP 3: PARALLEL SOLUTION ATTEMPTS (DIAMOND FORK)
        # Three independent approaches to mitigate misinterpretation risk
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""SOLUTION ATTEMPT 1: LITERAL NARRATIVE SEQUENCE

Using ONLY the chronological or narrative order presented in the original problem, simulate each step exactly as described. Do not reinterpret relationships — follow the text literally.

Start from initial state, apply each action in order, and compute the final result. Show all intermediate values with units.

Example: 'Morning: 15 cups → Afternoon: +25 cups → Evening: ? cups → Total needed: 60 cups → Subtract given: 60 - 40 = 20'

Output ONLY the final numerical answer at the end, prefixed with 'ANSWER: '""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""SOLUTION ATTEMPT 2: MATHEMATICAL MODELING

Ignore narrative order. Extract all mathematical relationships from the decomposition and build equations or expressions.

Define variables if needed. Solve algebraically or through direct computation. Show your work step by step.

Example: 'Let x = final feeding. Total needed = 20 chickens × 3 cups = 60. Given: 15 + 25 = 40. Therefore x = 60 - 40 = 20.'

Output ONLY the final numerical answer at the end, prefixed with 'ANSWER: '""",
                context=classification
            ),
            self.generate(
                instruction=f"""SOLUTION ATTEMPT 3: UNIT-AWARE SIMULATION WITH CONSTRAINTS

Simulate the problem while explicitly tracking units and enforcing real-world constraints from the decomposition (e.g., no negative quantities, whole units only).

At each step, verify: 
- Are units consistent? 
- Does the result make physical sense? 
- Does it violate any stated or implicit constraints?

If a step produces an invalid result (e.g., negative cups), adjust interpretation and note the correction.

Output ONLY the final numerical answer at the end, prefixed with 'ANSWER: '""",
                context=decomposition
            )
        )

        # STEP 4: ENSEMBLE SYNTHESIS — COMPARE, VALIDATE, SELECT
        synthesized = await self.ensemble(
            instruction="""You are given three independent solution attempts for the same math problem. Your task:

1. EXTRACT NUMERICAL ANSWERS: Identify the final answer from each attempt (look for 'ANSWER: X').
2. COMPARE: Are they identical? If not, which differ and why?
3. VALIDATE: Cross-check each against the original problem's constraints and decomposition. Does the answer make sense? Are units correct? Is it physically plausible?
4. RESOLVE: If consensus (2 or 3 agree), select that answer. If all differ, pick the one that best satisfies constraints and mathematical soundness.
5. OUTPUT: State the final answer as a single number. If uncertain, state the most defensible answer with brief justification.

Example output: '60' or '20 — because two methods agree and unit tracking confirms feasibility'""",
            contexts_list=solution_attempts
        )

        # STEP 5: REVISION LOOP — SANITY CHECK AND CORRECT IF NEEDED
        final_answer = synthesized
        for _ in range(2):  # Allow up to 2 revision cycles
            validation = await self.generate(
                instruction=f"""SANITY CHECK: Is this answer plausible given the original problem?

Answer to check: {final_answer}

Verify:
- Does it match the expected magnitude? (e.g., not 1000 when problem involves small quantities)
- Does it satisfy all constraints from decomposition? (e.g., non-negative, whole numbers if required)
- Is the unit correct? (e.g., cups, not chickens)
- Does it answer the exact question asked?

If any issue is found, explain the error and what correction is needed. If no issue, output 'VALID'.""",
                context=decomposition
            )

            if "VALID" in validation.upper():
                break
            else:
                # Revise using feedback
                final_answer = await self.revise(
                    instruction=f"""REVISE BASED ON VALIDATION FEEDBACK:

Validation feedback: {validation}

Re-examine your solution. Correct any misinterpretations, recalculate with proper constraints, and output ONLY the corrected numerical answer prefixed with 'ANSWER: '.

Common fixes:
- Reorder operations
- Reinterpret ambiguous phrases
- Apply missing constraints
- Convert units""",
                    context=final_answer
                )
                # Extract just the number from revised output for next validation
                match = re.search(r'ANSWER:\s*([0-9.]+)', final_answer)
                if match:
                    final_answer = match.group(1)

        # STEP 6: FINAL EXTRACTION AND CLEANUP
        clean_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below. Remove all units, labels, and explanations. Output must be a single number (integer or decimal).

If multiple numbers appear, select the one that directly answers the original question.

Example inputs: 
- 'ANSWER: 20 cups' → Output: '20'
- 'The result is 60.5' → Output: '60.5'
- 'After revision, we get 15' → Output: '15'

Be precise. No text. Just the number.""",
            context=final_answer
        )

        return clean_answer.strip()