# Workflow ID: mgsmbn_53_0
# Benchmark: mgsmbn
# Data Indices: [129, 82]

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

        # PHASE 1: NARRATIVE RECONSTRUCTION (Parallel Interpretation Generation)
        narrative_analysis = await self.generate(
            instruction="""Thoroughly deconstruct the Bengali word problem into its narrative components. Identify:
1. All entities (people, objects, animals) and their initial quantities.
2. Temporal sequence of events - what happens first, next, last.
3. Actions that modify quantities (add, remove, split, combine).
4. Hidden assumptions or implied constraints (e.g., "can't have negative frogs").
5. Units of measurement and their consistency throughout.
6. Ambiguous phrases that could have multiple interpretations.

Output in this exact format:
Entities: [list with initial quantities]
Timeline: [ordered list of events with quantity changes]
Ambiguities: [list of phrases with possible interpretations]
Constraints: [list of implicit rules]
Units: [list of units and where they appear]""",
            context=""
        )

        # Generate multiple interpretations for ambiguous phrases
        ambiguity_resolution = await self.generate(
            instruction=f"""Given the identified ambiguities:
{narrative_analysis}

Generate TWO distinct interpretations of the problem:
INTERPRETATION A: Most literal reading of the text.
INTERPRETATION B: Context-aware reading considering real-world constraints.

For each interpretation, reconstruct the full event timeline with explicit quantities and operations.
Format each as:
[Interpretation Name]
- Initial state: [description]
- Event 1: [action] → [new state]
- Event 2: [action] → [new state]
...
- Final query: [what is being asked]""",
            context=narrative_analysis
        )

        # PHASE 2: MATHEMATICAL FORMALIZATION (Parallel Path Processing)
        interpretations = re.split(r'INTERPRETATION [A-Z]:', ambiguity_resolution)[1:]
        interpretations = [f"INTERPRETATION {chr(65+i)}:{text.strip()}" for i, text in enumerate(interpretations) if text.strip()]

        if len(interpretations) < 2:
            # Fallback: create synthetic alternative if only one interpretation generated
            interpretations.append(ambiguity_resolution)
            interpretations.append(await self.generate(
                instruction="Create an alternative interpretation by assuming all quantity changes are cumulative rather than sequential.",
                context=narrative_analysis
            ))

        # Process each interpretation in parallel
        formalization_tasks = []
        for i, interpretation in enumerate(interpretations[:2]):  # Limit to 2 for efficiency
            task = self.generate(
                instruction=f"""Convert this interpretation into mathematical operations:
{interpretation}

Requirements:
1. Define variables for unknowns.
2. Write equations or step-by-step arithmetic for each event.
3. Track units at every step (e.g., 'frogs', 'minutes').
4. Show intermediate results.
5. Highlight any assumptions made.

Output format:
Mathematical Model:
[Equations or steps with units]
Intermediate Results:
[Step 1: ... = ... units]
[Step 2: ... = ... units]
...
Final Calculation:
[Expression] = [numerical answer] [units]""",
                context=interpretation
            )
            formalization_tasks.append(task)

        formalized_solutions = await asyncio.gather(*formalization_tasks)

        # PHASE 3: VALIDATION & ENSEMBLE
        validated_solutions = []
        for i, solution in enumerate(formalized_solutions):
            validated = await self.revise(
                instruction=f"""Critically validate this solution:
{solution}

Checklist:
1. Do units remain consistent throughout? (e.g., no adding frogs to minutes)
2. Are all intermediate results non-negative? (unless context allows negatives)
3. Is the final answer an integer if counting discrete objects?
4. Does the answer satisfy real-world constraints from the narrative?
5. Are there any arithmetic errors?

If any issues found, revise the solution with corrections. If no issues, return 'VALID: ' followed by the original solution.
Output only the validated solution or 'VALID: ' prefix.""",
                context=solution
            )
            validated_solutions.append(validated)

        # Ensemble: Select best solution based on validation and consistency
        final_answer = await self.ensemble(
            instruction="""Select the best solution based on:
1. Mathematical correctness (validated solutions preferred).
2. Consistency with original problem narrative.
3. Unit tracking integrity.
4. Adherence to real-world constraints.

If both solutions are valid, choose the one with clearer step-by-step reasoning.
If one solution has validation errors, choose the other.
If both have errors, synthesize a new solution combining correct elements.

Output ONLY the final numerical answer as a single number (integer or decimal). NO units, NO explanation.""",
            contexts_list=validated_solutions
        )

        # PHASE 4: SANITY CHECK & FINAL REVISION
        # Extract number from final_answer (in case ensemble included text)
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if number_match:
            extracted_number = number_match.group()
            # Verify it makes sense in context
            sanity_check = await self.generate(
                instruction=f"""Verify this answer: {extracted_number}
Against original problem: {self.problem_text}

Is this answer:
- Positive? (unless context allows negative)
- Integer if counting discrete objects?
- Within plausible range? (e.g., not 1000 frogs if problem mentions dozens)

If answer fails sanity check, return 'REJECT'. Otherwise, return 'ACCEPT: {extracted_number}'""",
                context=""
            )
            
            if "REJECT" in sanity_check:
                # Fallback: Direct calculation with explicit constraints
                final_answer = await self.generate(
                    instruction=f"""Original problem: {self.problem_text}

Recalculate with strict constraints:
1. Answer must be a positive number.
2. If counting objects, answer must be integer.
3. Show only the final number.

Output ONLY the numerical answer.""",
                    context=""
                )
                number_match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
                if number_match:
                    final_answer = number_match.group()
                else:
                    final_answer = "0"  # Ultimate fallback
            else:
                final_answer = extracted_number
        else:
            final_answer = "0"  # Fallback if no number found

        return final_answer