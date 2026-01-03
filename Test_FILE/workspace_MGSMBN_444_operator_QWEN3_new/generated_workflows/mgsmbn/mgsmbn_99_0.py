# Workflow ID: mgsmbn_99_0
# Benchmark: mgsmbn
# Data Indices: [124, 190]

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

        # PHASE 1: DECOMPOSE — Extract structured problem semantics
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math word problem. Identify and categorize:

1. ENTITIES: List all actors (people, animals, objects) and their roles.
2. QUANTITIES: Extract all numerical values and what they represent (include units: টাকা, ফ্রাই, ঘণ্টা, etc.)
3. ACTIONS: Chronologically list all events that change quantities (eating, stealing, investing, sharing, etc.)
4. RELATIONSHIPS: Note proportional/fractional relationships (half, triple, two-thirds, etc.)
5. TARGET: What is the unknown we're solving for?
6. CONSTRAINTS: Any implicit rules (no negative items, whole people, etc.)

Format output as a structured markdown list with clear section headers. Be exhaustive — missing one detail can break the solution.""",
            context=""
        )

        # PHASE 2: EXPLORE — Parallel solution strategies
        forward_solution, backward_solution, proportional_solution = await asyncio.gather(
            self.generate(
                instruction=f"""SOLVE FORWARD from initial state:

Using this decomposition:
{decomposition}

Assume the unknown starts as variable X. Apply each action IN CHRONOLOGICAL ORDER as described in the problem. Write algebraic expressions for each step. Show all intermediate calculations. Maintain unit tracking. End with an equation you can solve for X.

CRITICAL: If any step produces fractional people, negative money, or impossible units, flag it as invalid.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""SOLVE BACKWARD from final state:

Using this decomposition:
{decomposition}

Start from the LAST known quantity mentioned in the problem (e.g., '5 left', 'final amount'). Reverse each action in REVERSE CHRONOLOGICAL ORDER. For each reversal: if original action was 'subtract 5', reverse is 'add 5'; if 'multiply by 3', reverse is 'divide by 3'; if 'take half', reverse is 'double'. Show reversed algebraic steps. Solve for initial unknown.

CRITICAL: Validate that reversed operations make sense (e.g., reversing 'ate half' requires the remainder to be even).""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""SOLVE USING PROPORTIONAL/RELATIONAL MODELING:

Using this decomposition:
{decomposition}

Ignore chronology. Focus on relationships: ratios, fractions, percentages, multiples. Set up equations based on proportional constraints (e.g., 'A is half of B', 'C is triple D'). Solve system of equations for unknown. Show substitution steps.

CRITICAL: Check that all entities and quantities from decomposition are accounted for in equations.""",
                context=decomposition
            )
        )

        # PHASE 3: SYNTHESIZE — Ensemble best solution
        candidate_solutions = [forward_solution, backward_solution, proportional_solution]
        synthesized = await self.ensemble(
            instruction="""SELECT AND SYNTHESIZE the most mathematically sound solution:

Evaluate each candidate on:
1. COMPLETENESS: Does it account for ALL entities, actions, and quantities from decomposition?
2. CONSISTENCY: Are units preserved? No fractional people or negative quantities?
3. LOGIC: Are operations applied in correct order (chronological or reversed as appropriate)?
4. VERIFIABILITY: Can you plug the answer back into the story and reproduce the final state?
5. CLARITY: Are steps shown and justified?

If one solution is clearly superior, select it. If multiple are valid, merge their strongest parts. Extract the FINAL NUMERICAL ANSWER as a single integer or decimal. Output ONLY the number — no units, no explanation.""",
            contexts_list=candidate_solutions
        )

        # PHASE 4: VERIFY — Simulate answer in original context
        verification = await self.generate(
            instruction=f"""VERIFY by forward simulation:

Assume the answer is {synthesized}. Now re-run the ENTIRE problem narrative from start to finish using this value. Show each step. Does it reproduce the final state described in the original problem? If not, identify exactly where it breaks.

Output format:
VERIFICATION: [Pass|Fail]
BREAKPOINT: [Description if fail]
CORRECTED ANSWER: [New value if fail, else same as input]""",
            context=f"Original decomposition:\n{decomposition}\n\nProposed answer: {synthesized}"
        )

        # Conditional revision loop (max 1 iteration for efficiency)
        final_answer = synthesized
        if "VERIFICATION: Fail" in verification:
            corrected = await self.revise(
                instruction=f"""REVISE based on verification failure:

Verification result:
{verification}

Re-solve the problem accounting for the identified breakpoint. Use the most appropriate strategy (forward/backward/proportional) based on the error. Show corrected step-by-step math. Output ONLY the final numerical answer.""",
                context=synthesized
            )
            # Extract number from corrected response (handles "Answer: 48" or "48" etc.)
            number_match = re.search(r'[\d\.]+', corrected)
            if number_match:
                final_answer = number_match.group(0)

        # Ensure output is clean number
        try:
            # Convert to float then to int if whole number, else keep as float
            num = float(final_answer)
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        except:
            # Fallback if all else fails
            return "0"