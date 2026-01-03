# Workflow ID: mgsmbn_91_0
# Benchmark: mgsmbn
# Data Indices: [36]

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
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into its mathematical components. Follow this exact structure:

1. Entities: List all objects, people, or quantities mentioned. Assign symbolic variables (e.g., B = blue ties, R = red ties).
2. Given Values: Extract all explicit numbers with their meanings and units (e.g., "প্রতি নীল টাই $40" → UnitPrice_B = 40 USD).
3. Relationships: Translate all comparative phrases into mathematical operations (e.g., "দ্বিগুণ" → R = 2 × B, "50% বেশি" → Price_R = 1.5 × Price_B).
4. Target: Identify exactly what is being asked (e.g., "মোট ব্যয়" → TotalCost = ?).
5. Ambiguities: Flag any unclear references or missing information.

Output in this exact format:
---
ENTITIES:
- [Variable] = [Description]

GIVEN:
- [Variable] = [Value] [Unit]

RELATIONSHIPS:
- [Equation or operation]

TARGET:
- [What to solve for]

AMBIGUITIES:
- [List any unclear terms or assumptions needed]
---""",
            context=""
        )

        # PHASE 2: COMPLEXITY ASSESSMENT & CONDITIONAL ESCALATION
        needs_deep_analysis = any(keyword in decomposition for keyword in [
            "দ্বিগুণ", "তিনগুণ", "%", "অপেক্ষা", "পরে", "আগে", "মোট", "অংশ", "ভগ্নাংশ", 
            "twice", "thrice", "percent", "compared to", "after", "before", "total", "fraction"
        ])

        if needs_deep_analysis:
            # PARALLEL ANALYSIS BRANCH
            math_model, sequence_model, unit_model = await asyncio.gather(
                self.generate(
                    instruction=f"""Based on this decomposition:
{decomposition}

Create a rigorous mathematical model:
- Convert all relationships into formal equations
- Define all variables explicitly
- Do NOT solve yet — only model relationships
- Include unit annotations for each variable
Output as numbered equations.""",
                    context=decomposition
                ),
                self.generate(
                    instruction=f"""Based on this decomposition:
{decomposition}

Create a chronological sequence of operations:
- List events in order they occur
- Assign step numbers
- Identify dependencies between steps
- Flag any circular dependencies
Output as numbered steps with dependency notes.""",
                    context=decomposition
                ),
                self.generate(
                    instruction=f"""Based on this decomposition:
{decomposition}

Perform unit consistency analysis:
- List every quantity with its unit
- Flag any unit mismatches
- Suggest necessary conversions
- Identify physically impossible values (negative people, fractional items when inappropriate)
Output as bullet points with [OK] or [ISSUE] tags.""",
                    context=decomposition
                )
            )

            # SYNTHESIZE PARALLEL ANALYSES
            solution_plan = await self.ensemble(
                instruction="""Synthesize these three analyses into a single, coherent solution plan:

1. Mathematical Model: Provides equations
2. Sequence Model: Provides execution order  
3. Unit Model: Provides consistency checks

Rules for synthesis:
- Prioritize mathematical correctness over sequence if conflict
- Enforce unit consistency — convert units if needed
- Resolve ambiguities by choosing most contextually plausible interpretation
- Output a numbered step-by-step plan with explicit calculations at each step
- End with FINAL_ANSWER: <number> on its own line

Format:
Step 1: [Action] → [Calculation] = [Result]
Step 2: [Action] → [Calculation] = [Result]
...
FINAL_ANSWER: [number]""",
                contexts_list=[math_model, sequence_model, unit_model]
            )
        else:
            # SIMPLE PROBLEMS: DIRECT MODELING
            solution_plan = await self.generate(
                instruction=f"""Based on this decomposition:
{decomposition}

Create a direct solution plan:
- Single step or minimal steps
- Explicit calculation
- End with FINAL_ANSWER: <number> on its own line

Format:
Step 1: [Action] → [Calculation] = [Result]
FINAL_ANSWER: [number]""",
                context=decomposition
            )

        # PHASE 3: ADVERSARIAL REVISION (ASSUME IT'S WRONG)
        verified_plan = await self.revise(
            instruction="""Adversarial review: Assume this solution contains at least one error. Your task:

1. Check arithmetic calculations step by step
2. Verify unit conversions and consistency
3. Validate order of operations (PEMDAS/BODMAS)
4. Confirm proportional relationships (percentages, ratios)
5. Ensure no physical impossibilities (negative quantities, fractional people when inappropriate)

If no error found, output exactly: "VERIFIED: [original plan]"
If error found, output: "CORRECTED: [fixed plan with explanation of fix]"

Be brutally honest — even small errors matter.""",
            context=solution_plan
        )

        # PHASE 4: ERROR CORRECTION LOOP (MAX 1 RETRY)
        if "error" in verified_plan.lower() or "fix" in verified_plan.lower():
            verified_plan = await self.revise(
                instruction="""This is a corrected solution plan. Perform an even more rigorous verification:

1. Focus especially on the area that was previously corrected
2. Recalculate all dependent steps
3. Confirm final answer matches target requirement
4. Output final version starting with "FINAL_VERIFIED:"

Format:
FINAL_VERIFIED:
[Corrected step-by-step plan]
FINAL_ANSWER: [number]""",
                context=verified_plan
            )

        # PHASE 5: ANSWER EXTRACTION
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the verified solution plan.

Rules:
- Look for line starting with "FINAL_ANSWER:" 
- If multiple numbers, select the one after "FINAL_ANSWER:"
- If no FINAL_ANSWER line, scan for the last numerical result
- Return ONLY the number, no units, no text
- If truly ambiguous, return 0

Example outputs: "800", "42.5", "0" """,
            context=verified_plan
        )

        # CLEAN EXTRACTION (REMOVE ANY REMAINING TEXT)
        # Extract first number from string
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if number_match:
            return float(number_match.group()) if '.' in number_match.group() else int(number_match.group())
        else:
            return 0