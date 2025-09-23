# Workflow ID: mgsmbn_121_0
# Benchmark: mgsmbn
# Data Indices: [127]

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
        import json

        # STEP 1: Deep Structural Classification
        classification = await self.generate(
            instruction="""Perform a comprehensive analysis of this Bengali math word problem. Output must be a detailed classification with the following structure:

1. PROBLEM_TYPE: Identify primary category (e.g., "rate_problem", "distribution", "comparison", "proportional_reasoning", "multi_entity_tracking"). Be specific.
2. REASONING_DEPTH: Estimate number of distinct calculation steps required (1, 2, 3+).
3. KEY_ENTITIES: List all actors/objects with their associated quantities and units (e.g., "Blake: 15 round trips, 100 yards per trip").
4. UNITS: List all units involved and any required conversions.
5. HIDDEN_STEPS: Identify any implicit calculations (e.g., "round trip = 2x distance", "must calculate total before difference").
6. CONSTRAINTS: Note real-world or mathematical constraints (e.g., "answer must be integer", "no negative values").
7. CONFIDENCE: Rate classification confidence (High/Medium/Low).
8. AMBIGUITIES: List any unclear phrases or potential misinterpretations.

Format output as clearly labeled sections. This classification will guide all subsequent reasoning.""",
            context=""
        )

        # STEP 2: Conditional Strategy Selection
        # Generate initial solution attempt based on classification
        initial_solution = await self.generate(
            instruction=f"""Using this classification:
{classification}

Generate a complete, step-by-step solution. Requirements:
- Show all mathematical operations explicitly.
- Track units at every step.
- Justify each calculation based on problem context.
- Handle hidden steps identified in classification.
- Format final answer as: "FINAL_ANSWER: <number>"
- If any step is ambiguous, state assumptions clearly.""",
            context=classification
        )

        # STEP 3: Parallel Validation Fork
        # Three independent validation perspectives
        validation_tasks = [
            self.revise(
                instruction=f"""UNIT CONSISTENCY AUDIT:
You are a unit-tracking specialist. Verify:
1. All quantities have correct units attached.
2. Units are consistent across operations (e.g., no adding yards to meters).
3. Final answer has appropriate unit (if specified).
4. Any unit conversions are mathematically correct.
Flag any unit-related errors. If none, state "UNIT_CHECK_PASSED".""",
                context=initial_solution
            ),
            self.revise(
                instruction=f"""ARITHMETIC VALIDATOR:
You are a meticulous calculator. Verify:
1. Each arithmetic operation is correct (show recalculations if needed).
2. Order of operations is respected.
3. Intermediate results match stated values.
4. Final answer derivation is flawless.
Flag any calculation errors. If none, state "MATH_CHECK_PASSED".""",
                context=initial_solution
            ),
            self.revise(
                instruction=f"""REALITY CHECKER:
You are a real-world plausibility auditor. Verify:
1. Answer makes sense in context (e.g., no negative distances, fractional people).
2. Magnitudes are reasonable (e.g., a child didn't run 10,000 miles).
3. Constraints from classification are satisfied.
4. Assumptions are justifiable.
Flag any implausibility. If none, state "PLAUSIBILITY_CHECK_PASSED".""",
                context=initial_solution
            )
        ]

        validation_results = await asyncio.gather(*validation_tasks)

        # STEP 4: Ensemble Synthesis with Conflict Resolution
        refined_solution = await self.ensemble(
            instruction="""SYNTHESIZE VALIDATION FEEDBACK:
You are a master problem-solver reconciling three expert reviews. Rules:
1. If all validators report "PASSED", extract the final answer unchanged.
2. If any validator flags an error, prioritize fixing it over preserving original answer.
3. For unit errors: correct unit handling and recalculate.
4. For math errors: redo affected calculations step-by-step.
5. For plausibility issues: adjust assumptions or flag as ambiguous.
6. If conflicts exist between validators, resolve by: Unit > Math > Plausibility priority.
7. Output must end with "FINAL_ANSWER: <number>" on its own line.
8. Preserve all reasoning - do not skip steps.""",
            contexts_list=[initial_solution] + validation_results
        )

        # STEP 5: Iterative Refinement (if needed)
        # Check if ensemble output still contains error flags
        if any(keyword in refined_solution.lower() 
               for keyword in ["error", "fix", "incorrect", "invalid", "conflict"]):
            
            # One refinement iteration
            refined_solution = await self.revise(
                instruction="""FINAL POLISH:
You are performing last-chance refinement. Requirements:
1. Address all remaining error flags from previous step.
2. Ensure answer is a single numerical value.
3. Remove all explanatory text except the final answer line.
4. If ambiguity remains, choose most mathematically consistent interpretation.
5. Output ONLY in format: "FINAL_ANSWER: <number>"

Example good output:
FINAL_ANSWER: 80""",
                context=refined_solution
            )

        # STEP 6: Answer Extraction
        final_answer = await self.summarize(
            instruction="""EXTRACT NUMERICAL ANSWER:
From the solution text, extract ONLY the final numerical answer. Rules:
1. Look for line starting with "FINAL_ANSWER: "
2. Extract the number (integer or decimal) after the colon.
3. If multiple numbers, choose the one explicitly labeled as final answer.
4. Return ONLY the number, no units, no text.
5. If extraction fails, return "0" as fallback.

Example input: "After calculating... FINAL_ANSWER: 80"
Example output: "80" """,
            context=refined_solution
        )

        return final_answer.strip()