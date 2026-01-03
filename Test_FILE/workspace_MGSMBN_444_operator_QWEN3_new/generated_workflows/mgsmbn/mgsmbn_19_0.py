# Workflow ID: mgsmbn_19_0
# Benchmark: mgsmbn
# Data Indices: [6]

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

        # === LAYER 1: SEMANTIC DECOMPOSITION ===
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Extract:

1. ENTITIES: All named or implied actors/objects (e.g., 'প্রোগ্রাম', 'মাস', 'ব্যক্তি').
2. QUANTITIES: All numerical values with their contextual descriptors (e.g., '60 বার', '30% হ্রাস').
3. RELATIONSHIPS: Temporal, causal, or mathematical relationships (e.g., 'তিনগুণ বেশি', 'হ্রাস পেয়েছিল').
4. CONSTRAINTS: Explicit or implicit real-world constraints (e.g., 'ডাউনলোড সংখ্যা ঋণাত্মক হতে পারে না').
5. GOAL: Precisely what is being asked (e.g., 'মোট ডাউনলোড সংখ্যা').

Format as a structured JSON-like outline with clear section headers. Be exhaustive.""",
            context=""
        )

        # === LAYER 2: PROBLEM CLASSIFICATION & STRATEGY SELECTION ===
        classification = await self.generate(
            instruction=f"""Based on the decomposition:
{decomposition}

Classify this problem into one primary type and justify:

- Sequential Operations (multiple dependent steps)
- Rate/Proportion (speed, unit price, scaling)
- Distribution/Division (sharing, remainders)
- Comparison (differences, "how many more")
- Multi-entity State Tracking (quantities changing over time)

Then, propose the optimal solution strategy:
- Required mathematical operations
- Order of operations
- Unit handling requirements
- Potential pitfalls specific to this problem

Output structured classification followed by strategy blueprint.""",
            context=decomposition
        )

        # === LAYER 3: PARALLEL MODELING BRANCHES ===
        # Generate 3 independent modeling approaches
        modeling_branches = await asyncio.gather(
            self.generate(
                instruction=f"""Build a step-by-step mathematical model using ALGEBRAIC REPRESENTATION:
- Assign variables to unknowns
- Write equations for each relationship
- Show substitution and simplification
- Track units at every step
Context: {decomposition}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Build a step-by-step mathematical model using CHRONOLOGICAL SIMULATION:
- Start from initial state
- Apply each operation in narrative order
- Maintain running totals with unit annotations
- Flag any unit conversions needed
Context: {decomposition}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Build a step-by-step mathematical model using DIMENSIONAL ANALYSIS:
- Identify all units and conversion factors
- Set up calculation as unit cancellation chain
- Verify dimensional consistency at each step
- Highlight any implicit unit assumptions
Context: {decomposition}""",
                context=classification
            )
        )

        # === LAYER 4: ENSEMBLE SYNTHESIS & CONFLICT RESOLUTION ===
        synthesized_model = await self.ensemble(
            instruction="""Synthesize the three modeling approaches into one coherent solution path:

1. If all three agree on core steps, merge them into a single streamlined process.
2. If conflicts exist, identify the source (e.g., unit handling, operation order).
3. Select the most rigorous approach based on: explicit unit tracking, step-by-step justification, and alignment with problem constraints.
4. Output the final unified model with numbered steps.

Format: "SYNTHESIZED MODEL: [step-by-step procedure]".""",
            contexts_list=modeling_branches
        )

        # === LAYER 5: EXECUTION WITH VERIFICATION HOOKS ===
        initial_solution = await self.generate(
            instruction=f"""Execute the synthesized model to compute the numerical answer:

{synthesized_model}

Requirements:
- Show ALL intermediate calculations
- Annotate each step with units
- Box the final numerical answer at the end
- If any step produces non-physical result (negative count, fractional person), apply real-world constraint and note adjustment""",
            context=synthesized_model
        )

        # === LAYER 6: REVERSE VALIDATION ===
        validation = await self.revise(
            instruction=f"""Perform reverse validation:

Assume the final answer is correct. Work backward through each step of the solution:
- Does each backward step logically reconstruct the prior state?
- Do all quantities remain consistent with original problem constraints?
- Are units preserved correctly in reverse?

If any inconsistency is found, identify the FIRST point of failure and propose correction.
If fully consistent, output 'VALIDATED'.""",
            context=initial_solution
        )

        # === LAYER 7: ITERATIVE REFINEMENT (if needed) ===
        final_solution = initial_solution
        if "inconsistency" in validation.lower() or "failure" in validation.lower():
            final_solution = await self.revise(
                instruction=f"""Revise the solution to fix the validation failure:

Validation feedback: {validation}

Requirements:
- Preserve correct parts of original solution
- Only modify steps that caused inconsistency
- Add explicit unit conversion if missing
- Re-validate internally before outputting""",
                context=initial_solution
            )

        # === LAYER 8: ANSWER EXTRACTION & SANITIZATION ===
        sanitized_answer = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this solution:

{final_solution}

Rules:
- Must be a single number (integer or decimal)
- Remove all units, commas, explanatory text
- If multiple numbers, select the one answering 'কত?' or 'মোট কত?'
- If answer is fractional, convert to decimal
- Output ONLY the number, nothing else""",
            context=final_solution
        )

        # Clean and return
        # Remove any non-numeric except decimal point
        clean_answer = re.sub(r'[^\d.]', '', sanitized_answer.strip())
        return clean_answer