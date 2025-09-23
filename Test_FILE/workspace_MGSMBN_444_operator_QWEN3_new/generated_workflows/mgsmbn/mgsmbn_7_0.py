# Workflow ID: mgsmbn_7_0
# Benchmark: mgsmbn
# Data Indices: [140, 120]

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
        semantic_analysis = await self.generate(
            instruction="""Perform deep semantic decomposition of the Bengali word problem. Extract and structure:

1. ENTITIES: List all named objects, people, animals, or quantities. For each, note:
   - Name/Identifier
   - Initial value (if given)
   - Role in the problem

2. RELATIONSHIPS: Map how entities relate:
   - Mathematical (e.g., "A is twice B")
   - Temporal (e.g., "first 6 hours, then next 6 hours")
   - Causal (e.g., "because X happened, Y changed")

3. OPERATIONS: Identify explicit and implicit mathematical operations:
   - Arithmetic (+, -, ×, ÷)
   - Proportional (fractions, percentages, ratios)
   - Temporal sequencing (order matters)

4. CONSTRAINTS: Note real-world or logical constraints:
   - Non-negative quantities
   - Integer-only results (e.g., number of bees)
   - Unit consistency (টাকা, ঘণ্টা, জিনিস)

5. GOAL: Explicitly state what is being asked (e.g., "মোট বয়স কত?" → total age)

Format output as clearly labeled sections. Be exhaustive. If something is ambiguous, state your assumption and why.""",
            context=""
        )

        # === LAYER 2: PARALLEL STRATEGY EXPLORATION ===
        strategy_algebraic, strategy_simulation, strategy_unit = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
Given semantic analysis:
{semantic_analysis}

Steps:
1. Assign variables to unknowns.
2. Translate relationships into equations.
3. Solve system of equations step by step.
4. Substitute known values.
5. Show all algebraic manipulations.

Output: Detailed solution with final numerical answer highlighted.""",
                context=semantic_analysis
            ),
            self.generate(
                instruction=f"""Solve using CHRONOLOGICAL SIMULATION:
Given semantic analysis:
{semantic_analysis}

Steps:
1. Break problem into time-ordered or operation-ordered steps.
2. Track state changes for each entity after each step.
3. Use tables or step-by-step logs if helpful.
4. Accumulate final result.

Output: Simulation log with final numerical answer highlighted.""",
                context=semantic_analysis
            ),
            self.generate(
                instruction=f"""Solve using UNIT & DIMENSIONAL ANALYSIS:
Given semantic analysis:
{semantic_analysis}

Steps:
1. Track units of all quantities (টাকা, ঘণ্টা, জিনিস, etc.).
2. Ensure unit consistency in operations.
3. Use unit cancellation to infer missing operations.
4. Validate that final answer has correct unit (if specified).

Output: Unit-tracking solution with final numerical answer highlighted.""",
                context=semantic_analysis
            )
        )

        # === LAYER 3: ENSEMBLE SYNTHESIS ===
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution attempts (algebraic, simulation, unit analysis) into one coherent answer.

Evaluation criteria:
1. CONSISTENCY: Does the solution align with extracted entities and relationships?
2. CONSTRAINT ADHERENCE: Does it respect real-world constraints (non-negative, integer if required)?
3. MATHEMATICAL SOUNDNESS: Are operations applied correctly? Order of operations respected?
4. COMPLETENESS: Does it address all parts of the problem?

If all three agree, select any and add confidence note.
If two agree, select the majority and explain why the third failed.
If all differ, pick the most complete and logically consistent, then revise it.

Output: Single synthesized solution with final numerical answer clearly stated.""",
            contexts_list=[strategy_algebraic, strategy_simulation, strategy_unit]
        )

        # === LAYER 4: ITERATIVE REFINEMENT (max 2 iterations) ===
        refined_solution = synthesized_solution
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""VALIDATE this solution against original problem:
{refined_solution}

Check:
1. Sentence-by-sentence alignment: Does each part of the problem have a corresponding calculation?
2. Arithmetic accuracy: Recompute key steps.
3. Unit and constraint compliance.
4. Answer format: Single numerical value?

If any issue found, describe it specifically. If perfect, say "VALIDATED".""",
                context=refined_solution
            )
            
            if "VALIDATED" in validation or "validat" in validation.lower():
                break
            else:
                refined_solution = await self.revise(
                    instruction=f"""REVISE based on validation feedback:
{validation}

Fix all identified issues. Maintain clarity. Show corrected steps.
Ensure final answer is numerically accurate and contextually appropriate.""",
                    context=refined_solution
                )

        # === LAYER 5: FINAL ANSWER EXTRACTION ===
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution below.

Rules:
- Must be a single number (integer or decimal).
- Strip all text, units, explanations.
- If multiple numbers, choose the one that directly answers the question.
- If no clear number, return "0" as fallback.

Example: If solution says "মোট বয়স 51 বছর", output "51".

Solution:
""" + refined_solution,
            context=refined_solution
        )

        # Clean and return final answer
        # Extract first number (integer or decimal) from string
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return match.group(0)
        else:
            return "0"  # Fallback