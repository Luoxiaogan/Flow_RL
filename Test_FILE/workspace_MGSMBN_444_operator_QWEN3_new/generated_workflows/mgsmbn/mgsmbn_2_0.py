# Workflow ID: mgsmbn_2_0
# Benchmark: mgsmbn
# Data Indices: [92, 52]

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

        # STEP 1: Comprehensive problem decomposition and classification
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem. Your task:

1. Identify and list ALL numerical values mentioned, with their contextual meaning (e.g., "7:13 ratio", "$5 weekly allowance").
2. Classify the problem type: Is it about ratios, sequences of transactions, rates, distributions, comparisons, or multi-entity tracking?
3. Extract the unknown: What exactly is being asked? Represent it symbolically if possible (e.g., "find X where X is initial amount").
4. Identify any implicit constraints or real-world assumptions (e.g., "can't have negative money", "must be whole number of people").
5. Outline the apparent sequence of operations or relationships implied by the narrative.

Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: Parallel solution path generation - Forward Simulation and Backward Inference
        forward_path, backward_path = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the problem decomposition:

{decomposition}

Attempt a FORWARD SIMULATION solution:
- Start from known initial values or given quantities.
- Apply operations in the chronological or logical order implied by the problem.
- Do NOT solve algebraically for unknowns — simulate forward only.
- Show each intermediate step with clear labeling.
- Track units throughout.
- If you encounter an unknown you can't resolve forward, note it and proceed with placeholders.
- Your final output should be a numerical answer or a clear statement of what's missing.

Focus on procedural execution, not algebraic rearrangement.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Based on the problem decomposition:

{decomposition}

Attempt a BACKWARD INFERENCE solution:
- Start from the final goal or known endpoint (e.g., "ended with $100").
- Work backwards through the operations, reversing each step (e.g., if problem says "added", you subtract).
- Solve for the unknown by reversing the implied sequence.
- Show each reversed step with clear labeling.
- Track units throughout.
- Your final output should be a numerical answer derived by backward reasoning.

Focus on algebraic or reverse-engineering approaches, not forward simulation.""",
                context=decomposition
            )
        )

        # STEP 3: Independent refinement of each path
        refined_forward = await self.revise(
            instruction="""Critically review this forward simulation solution:

1. Verify that each step follows logically from the previous one.
2. Check unit consistency — are units preserved or converted correctly?
3. Validate arithmetic calculations — redo any critical math.
4. Ensure no steps were skipped or assumed without basis.
5. If the solution is incomplete or incorrect, fix it by adding missing steps or correcting errors.
6. Ensure the final answer is explicitly stated as a single numerical value.

Improve clarity, precision, and mathematical rigor.""",
            context=forward_path
        )

        refined_backward = await self.revise(
            instruction="""Critically review this backward inference solution:

1. Verify that reversing each operation is mathematically valid (e.g., subtraction for addition, division for multiplication).
2. Check that the starting point for backward reasoning is correctly identified from the problem.
3. Validate arithmetic calculations — redo any critical math.
4. Ensure symbolic manipulations (if any) are algebraically sound.
5. If the solution is incomplete or incorrect, fix it by adding missing steps or correcting errors.
6. Ensure the final answer is explicitly stated as a single numerical value.

Improve clarity, precision, and mathematical rigor.""",
            context=backward_path
        )

        # STEP 4: Ensemble synthesis with validation-aware selection
        synthesized = await self.ensemble(
            instruction="""You are given two solution paths for the same Bengali math problem:

PATH A (Forward Simulation):
---
{forward}
---

PATH B (Backward Inference):
---
{backward}
---

Your task:

1. Compare both paths. Do they arrive at the same numerical answer? If yes, that answer is likely correct.
2. If they differ, analyze why:
   - Which path better respects the problem's narrative structure?
   - Which path has fewer logical leaps or assumptions?
   - Which path handles units and constraints more accurately?
3. Validate the winning answer by plugging it back into the original problem context. Does it satisfy all conditions?
4. If both are flawed, synthesize a new answer by combining the valid parts of each.
5. Output ONLY the final numerical answer as a single integer or decimal. No explanation, no units, no text.

Example output: 42""",
            contexts_list=[refined_forward, refined_backward]
        )

        # STEP 5: Final validation and revision loop (up to 2 iterations)
        final_answer = synthesized
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Validate this answer against the original problem:

Proposed Answer: {final_answer}

Original Problem: 
{self.problem_text}

Perform these checks:

1. Substitute the answer back into the problem's narrative. Does it logically satisfy all stated conditions?
2. Verify unit consistency — does the answer have the right unit (implied or explicit)?
3. Check for real-world plausibility — e.g., no negative quantities where impossible, whole numbers for countable items.
4. Recompute critical steps independently to confirm arithmetic.
5. If any inconsistency is found, state it clearly and suggest the corrected value.

If valid, respond with "VALID". If invalid, respond with "INVALID: [reason] and corrected value should be X".""",
                context=final_answer
            )

            if "VALID" in validation:
                break
            else:
                # Extract corrected value if suggested
                corrected_match = re.search(r"corrected value should be ([\d\.]+)", validation)
                if corrected_match:
                    final_answer = corrected_match.group(1)
                else:
                    # If no correction suggested, revise using validation feedback
                    final_answer = await self.revise(
                        instruction=f"""Revise the answer based on this validation feedback:

{validation}

Original problem context:
{self.problem_text}

Output ONLY the corrected numerical value. No explanation.""",
                        context=final_answer
                    )
                # Continue to next iteration for re-validation

        return final_answer