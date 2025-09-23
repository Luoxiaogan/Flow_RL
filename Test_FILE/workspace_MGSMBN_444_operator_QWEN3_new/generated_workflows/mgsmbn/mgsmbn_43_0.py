# Workflow ID: mgsmbn_43_0
# Benchmark: mgsmbn
# Data Indices: [29]

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

        # STEP 1: SEMANTIC FRAMING — Extract entities, actions, quantities, relationships
        semantic_frame = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math problem. Identify and structure:

1. ENTITIES: All people, objects, or groups mentioned (e.g., "জন", "ট্রেন", "বই").
2. QUANTITIES: All numbers with their units and what they measure (e.g., "60 মাইল" → total distance).
3. ACTIONS: Verbs indicating operations (e.g., "দৌড়ান" → running, implies speed/distance/time).
4. RELATIONSHIPS: Proportional, sequential, or comparative links (e.g., "অর্ধেক" → half, "প্রথম দিনে...অন্য দুদিন" → sequence).
5. GOAL: What is being asked? (e.g., "কত দ্রুত" → speed in mph?).

Output in this exact format:
---
**Entities:**
- [Entity 1]: [Role/Description]
- [Entity 2]: [Role/Description]

**Quantities:**
- [Number] [Unit]: [What it represents]

**Actions:**
- [Action 1]: [Implied operation]
- [Action 2]: [Implied operation]

**Relationships:**
- [Relationship 1]: [Mathematical implication]
- [Relationship 2]: [Mathematical implication]

**Goal:**
[Explicit restatement of what to solve for]
---
""",
            context=""
        )

        # STEP 2: COMPLEXITY CLASSIFICATION — Is this simple or complex?
        complexity_analysis = await self.generate(
            instruction=f"""Analyze the semantic frame below and classify problem complexity:

Semantic Frame:
{semantic_frame}

Classify as:
- "SIMPLE" if: single operation, no hidden steps, no unit conversions, no proportional reasoning.
- "COMPLEX" if: multiple steps, hidden relationships, unit conversions, proportions, or ambiguous phrasing.

Output ONLY one word: "SIMPLE" or "COMPLEX".""",
            context=semantic_frame
        )

        # STEP 3: ADAPTIVE BRANCHING
        if "SIMPLE" in complexity_analysis.upper():
            # Direct path for simple problems
            direct_solution = await self.generate(
                instruction=f"""Solve this problem directly using the semantic frame. Show:

1. Known values (from frame).
2. Required operation (add/subtract/multiply/divide).
3. Step-by-step calculation.
4. Final answer with unit.

Semantic Frame:
{semantic_frame}

Output must end with: "ANSWER: [number]".""",
                context=semantic_frame
            )

            validated_solution = await self.revise(
                instruction="""Verify this solution:
- Are units consistent?
- Is arithmetic correct?
- Does it answer the goal?
- Are there any hidden steps missed?

If errors, fix them. Keep final "ANSWER: [number]" format.""",
                context=direct_solution
            )

            solutions_to_ensemble = [validated_solution]

        else:
            # Parallel solution paths for complex problems
            strategy_instructions = [
                f"""Solve using ALGEBRAIC MODELING:
- Define variables for unknowns.
- Write equations based on relationships.
- Solve step-by-step.
- Verify against total quantities.

Semantic Frame:
{semantic_frame}

End with "ANSWER: [number]".""",

                f"""Solve using UNIT-RATE DECOMPOSITION:
- Find rate per unit (e.g., speed, price per item).
- Apply to given quantities.
- Scale or combine as needed.

Semantic Frame:
{semantic_frame}

End with "ANSWER: [number]".""",

                f"""Solve using CHRONOLOGICAL SIMULATION:
- Simulate the scenario step-by-step as described.
- Track quantities after each action.
- Aggregate to final result.

Semantic Frame:
{semantic_frame}

End with "ANSWER: [number]"."""
            ]

            # Generate 3 solution paths in parallel
            raw_solutions = await asyncio.gather(
                *[self.generate(instruction=instr, context=semantic_frame) for instr in strategy_instructions]
            )

            # Validate each solution in parallel
            validated_solutions = await asyncio.gather(
                *[self.revise(
                    instruction="""CRITICALLY VALIDATE:
- Check unit consistency at every step.
- Verify arithmetic (recalculate key steps).
- Ensure all relationships from semantic frame are respected.
- Flag if answer contradicts problem constraints (e.g., negative people).
- If error, correct it. Preserve "ANSWER: [number]" format.""",
                    context=sol
                ) for sol in raw_solutions]
            )

            solutions_to_ensemble = validated_solutions

        # STEP 4: ENSEMBLE — Synthesize or select best answer
        final_answer_draft = await self.ensemble(
            instruction="""You are given 1 or 3 candidate solutions. Your task:

1. If only one solution: return it unchanged.
2. If three solutions:
   a. Compare numerical answers. If all match, return the most clearly reasoned.
   b. If they differ, identify which solution best respects:
      - Unit consistency
      - All relationships from semantic frame
      - Real-world constraints (no negative/fractional people unless allowed)
   c. Return the best solution. If tie, prefer algebraic approach.

Output must include "ANSWER: [number]" at the end.""",
            contexts_list=solutions_to_ensemble
        )

        # STEP 5: EXTRACT CLEAN NUMERICAL ANSWER
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below.

Rules:
- Find the line containing "ANSWER: [number]".
- Extract only the number (integer or decimal).
- If multiple numbers, choose the one that directly answers the original question.
- Output NOTHING else — no units, no text, no explanation.

Example: If text says "ANSWER: 10.5", output "10.5".""",
            context=final_answer_draft
        )

        return final_answer.strip()