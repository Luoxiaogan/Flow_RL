# Workflow ID: mgsmbn_55_0
# Benchmark: mgsmbn
# Data Indices: [174, 22]

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

        # PHASE 1: Problem Understanding & Classification
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and produce a structured breakdown:

1. **Problem Type Classification**: Identify if this is: Sequential, Proportional (Ratio/Percentage), Distribution, Comparison, Rate-Based, or Multi-Entity Tracking. Explain why.

2. **Entity Extraction**: List all:
   - Named entities (people, objects)
   - Numerical values with their contextual meaning (e.g., "7" → "7 additional flowers")
   - Units (টাকা, বছর, টি, etc.)
   - Temporal markers (বছর পরে, এখন থেকে, etc.)

3. **Relationship Mapping**: Describe mathematical relationships implied by verbs and phrases (e.g., "বেশি" → addition, "অনুপাত" → ratio, "মোট" → sum).

4. **Unknown Identification**: Clearly state what is being asked for (the unknown).

5. **Constraints**: Note any real-world constraints (e.g., non-negative, integer-only, unit consistency).

Format output as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # PHASE 2: Dynamic Strategy Selection
        strategy_instruction = await self.generate(
            instruction=f"""Based on this analysis:
{problem_analysis}

Generate a DETAILED, STEP-BY-STEP solving strategy tailored to this specific problem type. Include:

- **Mathematical Modeling**: How to translate the Bengali narrative into equations or operations.
- **Step Sequence**: Exact order of calculations, with justification for each step.
- **Intermediate Variables**: What to solve for first, second, etc.
- **Unit Handling**: How to track and convert units if needed.
- **Verification Points**: Where to sanity-check intermediate results.

If this is a Ratio/Proportional problem, explicitly set up variables (e.g., 7x, 11x). If Sequential, map the timeline. If Distribution, define the sharing logic.

Output ONLY the strategy, in clear numbered steps.""",
            context=problem_analysis
        )

        # PHASE 3: Parallel Solution Attempts (Adaptive)
        # Generate 2 solution paths: one strictly following strategy, one alternative approach
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Execute this strategy EXACTLY:
{strategy_instruction}

Show ALL work:
1. Write down known values and relationships.
2. Perform calculations step by step.
3. Maintain full precision (no rounding until final answer).
4. Track units throughout.
5. Box the final numerical answer at the end.

Output format: Step-by-step calculation → Final Answer: [number]""",
                context=strategy_instruction
            ),
            self.generate(
                instruction=f"""Solve the problem using an ALTERNATIVE approach (e.g., if strategy uses algebra, use arithmetic; if forward calculation, try backward reasoning). Still respect the problem's semantics and constraints.

Show ALL work:
1. Different modeling approach.
2. Same precision and unit tracking.
3. Box final answer.

Output format: Alternative Approach → Step-by-step → Final Answer: [number]""",
                context=problem_analysis
            )
        )

        # PHASE 4: Ensemble Synthesis & Conflict Resolution
        final_answer = await self.ensemble(
            instruction="""You are given 2 solution attempts for the same Bengali math problem. Your task:

1. **Compare Results**: Do both solutions arrive at the same numerical answer? If yes, that's your answer.
2. **If Conflict**: Identify which solution has fewer logical gaps, better unit handling, or more faithful semantic modeling. Choose that one.
3. **Extract Answer**: The final answer is ALWAYS a single number (integer or decimal). Ignore all text except the boxed answer.
4. **No Compromise**: If both are wrong, pick the least wrong, but note this is rare.

Output ONLY the numerical answer. No explanations.""",
            contexts_list=solution_attempts
        )

        # PHASE 5: Contextual Sanity Check & Final Revision
        sanitized_answer = await self.revise(
            instruction=f"""You are given a numerical answer for a Bengali word problem. Apply STRICT real-world sanity checks:

1. **Entity Constraints**: If counting discrete objects (flowers, people), answer MUST be non-negative integer.
2. **Temporal Logic**: If projecting future values (e.g., "10 years later"), answer MUST be greater than current value.
3. **Unit Consistency**: Answer must match expected unit (e.g., বছর for age, টাকা for money).
4. **Magnitude Check**: Does the number make sense? (e.g., 1000-year-old person? 0.5 flowers? Reject.)

If answer passes all checks, return it unchanged.
If it fails, revise by:
- Rounding to nearest integer (if fractional but should be whole)
- Adding missing temporal offset (e.g., forgot "+10 years")
- Correcting sign (negative → positive if context forbids negatives)

Output ONLY the final sanitized numerical value. No text.""",
            context=final_answer
        )

        # Extract numerical value using regex (handles "Final Answer: 15" or just "15")
        match = re.search(r'[\d\.]+', sanitized_answer)
        if match:
            return float(match.group(0)) if '.' in match.group(0) else int(match.group(0))
        else:
            # Fallback: return raw if no number found (shouldn't happen)
            return sanitized_answer.strip()