# Workflow ID: mgsmbn_122_0
# Benchmark: mgsmbn
# Data Indices: [99]

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

        # PHASE 1: PARALLEL DECOMPOSITION — Extract problem anatomy from 3 angles
        entity_extraction, sequence_analysis, target_identification = await asyncio.gather(
            self.generate(
                instruction="""Extract all numerical entities and their semantic roles. For each number:
                - What does it quantify? (distance, time, rate, count, etc.)
                - What are its units? (মাইল, ঘণ্টা, টাকা, etc.)
                - What is its role in the operation? (multiplier, divisor, base, etc.)
                Format as: [Entity]: [Value] [Unit] → [Role] → [Contextual Description]""",
                context=""
            ),
            self.generate(
                instruction="""Analyze temporal or logical sequencing. Identify:
                - Chronological order of events (first, then, after, total time)
                - Conditional dependencies (if...then, unless, until)
                - Implicit time boundaries or phase transitions
                Output as a timeline or flowchart in text form.""",
                context=""
            ),
            self.generate(
                instruction="""Identify the exact target variable being asked for. Determine:
                - What is the question literally asking? (Copy the exact phrase)
                - What mathematical quantity does this correspond to? (total distance, remaining money, etc.)
                - What units should the answer have?
                - Are there any constraints on the answer format? (integer, decimal, rounded?)""",
                context=""
            )
        )

        # PHASE 2: DYNAMIC INSTRUCTION SYNTHESIS — Build adaptive solving prompts
        synthesis_context = f"""
Entities:
{entity_extraction}

Sequence:
{sequence_analysis}

Target:
{target_identification}
"""

        # PHASE 3: PARALLEL SOLUTION GENERATION — Three independent solving strategies
        algebraic_approach, narrative_approach, unit_analysis_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Solve algebraically. Steps:
1. Define variables for unknowns.
2. Write equations based on relationships in the problem.
3. Solve step by step, showing substitutions.
4. Box the final answer.
Context:
{synthesis_context}""",
                context=synthesis_context
            ),
            self.generate(
                instruction=f"""Solve by simulating the narrative chronologically. Steps:
1. Start from initial state.
2. Apply each event in sequence as described.
3. Track cumulative changes.
4. Arrive at final state matching the question.
Context:
{synthesis_context}""",
                context=synthesis_context
            ),
            self.generate(
                instruction=f"""Solve by dimensional/unit analysis. Steps:
1. Write down all quantities with units.
2. Cancel units through multiplication/division to reach target unit.
3. Show unit arithmetic explicitly.
4. Verify final unit matches target.
Context:
{synthesis_context}""",
                context=synthesis_context
            )
        )

        # PHASE 4: ENSEMBLE SELECTION WITH CRITIQUE — Choose best or synthesize
        final_answer = await self.ensemble(
            instruction="""Evaluate the three solution attempts:
1. Check mathematical correctness: Are calculations accurate?
2. Check linguistic fidelity: Does solution respect Bengali phrasing and intent?
3. Check contextual plausibility: Is answer reasonable? (e.g., no negative apples)
4. Check unit consistency: Are units preserved and appropriate?

If all agree, return any. If they conflict:
- Identify the most consistent solution.
- Generate a reconciliation that fixes discrepancies.
- Return the reconciled answer.

Output ONLY the final numerical answer, no explanation.""",
            contexts_list=[algebraic_approach, narrative_approach, unit_analysis_approach]
        )

        # PHASE 5: SANITY CHECK REVISION — Final guardrail
        verified_answer = await self.revise(
            instruction="""Perform final sanity check:
- Is the number plausible? (e.g., human running 500 miles in 7 hours? No.)
- Are units correct and consistent?
- Does it match the target variable's expected format?
- Would a grade school student find this reasonable?

If any issue, correct it. Otherwise, return unchanged.
Output ONLY the numerical value.""",
            context=final_answer
        )

        # Extract numerical value (handles cases where LLM adds text)
        match = re.search(r'[\d,]+\.?\d*', verified_answer.replace(',', ''))
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return raw if no number found (shouldn't happen)
            return verified_answer.strip()