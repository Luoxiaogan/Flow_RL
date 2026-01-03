# Workflow ID: mgsmbn_42_0
# Benchmark: mgsmbn
# Data Indices: [168, 185]

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

        # STEP 1: Problem Typing and Entity Extraction
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and output structured information in this exact format:

[Type]: <one of: sequential, rate, proportional, distribution, comparison, multi-entity>
[Entities]: 
- <Entity 1>: <value> <unit> (<description>)
- <Entity 2>: <value> <unit> (<description>)
...
[Constraints]: 
- <Constraint 1 description>
- <Constraint 2 description>
...
[Unknown]: <what needs to be calculated>

Be exhaustive. Identify all numbers, their meanings, and relationships. Flag any ambiguous terms. Consider real-world plausibility constraints (e.g., no negative people, fractional items may be invalid).""",
            context=""
        )

        # STEP 2: Parallel Solution Pathway Generation
        solution_pathways = await asyncio.gather(
            self.generate(
                instruction=f"""Using this problem analysis:
{problem_analysis}

Solve using ARITHMETIC SIMULATION approach:
- Simulate the scenario step by step as if acting it out chronologically.
- Track running totals after each operation.
- Explicitly state what each calculation represents.
- Preserve unit consistency throughout.
- Show all intermediate values.
- Box final answer at end.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Using this problem analysis:
{problem_analysis}

Solve using ALGEBRAIC MODELING approach:
- Define variables for unknowns.
- Set up equations based on relationships.
- Solve equations step by step.
- Substitute known values.
- Show algebraic manipulations.
- Box final answer at end.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Using this problem_analysis:
{problem_analysis}

Solve using UNIT PROPAGATION & DIMENSIONAL ANALYSIS:
- Focus on units to determine operations (e.g., if answer needs 'times', find what divides into total).
- Track unit transformations through each step.
- Use proportional reasoning where applicable.
- Justify each operation by unit consistency.
- Box final answer at end.""",
                context=problem_analysis
            )
        )

        # STEP 3: Validation and Revision Loop (max 2 iterations per pathway)
        revised_pathways = []
        for pathway in solution_pathways:
            current = pathway
            for _ in range(2):  # Max 2 revision rounds
                validation = await self.revise(
                    instruction="""Critically validate this solution:
- Check every arithmetic operation for correctness.
- Verify unit consistency at each step.
- Ensure no invalid quantities (negative people, fractional indivisible items).
- Confirm final answer matches what was asked.
- If error found, fix it and explain the correction.
- If no error, return 'VALIDATED' at end.
- Preserve step-by-step reasoning.""",
                    context=current
                )
                if "VALIDATED" in validation:
                    revised_pathways.append(validation)
                    break
                current = validation
            else:
                # If still not validated after 2 tries, keep last revision
                revised_pathways.append(current)

        # STEP 4: Ensemble Synthesis
        final_answer_candidate = await self.ensemble(
            instruction="""Synthesize the best answer from these revised solutions:
1. If all solutions agree numerically, output that number.
2. If they disagree, select the solution that:
   - Explicitly handles all constraints from problem analysis
   - Shows complete step-by-step reasoning
   - Maintains unit consistency throughout
   - Has no logical gaps
3. Extract ONLY the final numerical value (no units, no text).
4. If no solution is fully consistent, output the most plausible number.""",
            contexts_list=revised_pathways
        )

        # STEP 5: Contextual Sanity Check
        sanity_check = await self.generate(
            instruction=f"""Given this final answer candidate: {final_answer_candidate}
And original problem: {self.problem_text}

Write a one-sentence explanation of how this answer fits the scenario. 
If the answer is implausible (e.g., negative count, fractional person, contradicts problem), respond with exactly: 'RETRY'
Otherwise, respond with exactly: 'OK'""",
            context=""
        )

        # STEP 6: Fallback Cascade if needed
        if "RETRY" in sanity_check:
            final_answer_candidate = await self.generate(
                instruction="""BRUTE FORCE RE-SOLVE:
List every known value from problem with its meaning.
Define the unknown precisely.
Write one mathematical operation at a time.
After each operation, state the new value and what it represents.
Continue until unknown is calculated.
Ensure unit consistency.
Ensure real-world plausibility.
Output ONLY the final numerical value. No text. No units.""",
                context=""
            )

        # STEP 7: Final Answer Extraction (ensure pure number)
        final_answer = await self.generate(
            instruction=f"""Extract ONLY the numerical value from this text: {final_answer_candidate}
Remove all units, labels, explanations, or text.
If decimal, preserve exact precision.
If fraction, convert to decimal.
Output nothing else — just the number.""",
            context=""
        )

        # Clean and return
        # Remove any non-numeric except decimal point and minus (though minus should be rare)
        cleaned = re.sub(r'[^\d\.-]', '', final_answer)
        return cleaned.strip()