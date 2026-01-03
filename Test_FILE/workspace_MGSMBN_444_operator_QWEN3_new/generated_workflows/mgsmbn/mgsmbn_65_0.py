# Workflow ID: mgsmbn_65_0
# Benchmark: mgsmbn
# Data Indices: [181, 54]

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

        # STEP 1: STRUCTURED ENTITY & RELATIONSHIP EXTRACTION
        entity_map = await self.generate(
            instruction="""Perform deep semantic parsing of the Bengali word problem. Extract and categorize:

1. ENTITIES: List all people, objects, or agents (e.g., Carlos, Benji, phones, boats)
2. QUANTITIES: Every numerical value with its associated entity and unit (e.g., "30 টাকা/ঘণ্টা for Carlos's boat")
3. ACTIONS: What each entity does, with timing/duration if applicable (e.g., "Carlos uses boat for 3 hours")
4. RELATIONSHIPS: Mathematical operations implied (e.g., "per hour" → multiplication, "total" → summation)
5. CONSTRAINTS: Real-world limits (e.g., no negative money, whole persons)
6. TARGET: What is being asked for (e.g., "total cost", "monthly payment")

Format as JSON-like structure with clear section headers. Be exhaustive — missing one number can break the solution.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION STRATEGY GENERATION (DIAMOND FORK)
        strategy_instructions = [
            """Apply CHRONOLOGICAL SIMULATION strategy:
- Model events in the order they occur in time
- For each time segment, calculate cost/quantity changes
- Accumulate totals step by step
- Track units at every stage (টাকা, ঘণ্টা, etc.)
- Example: If Carlos uses boat 3 hours at 30/hr, calculate 3*30=90 before adding Benji's cost
Output detailed step-by-step calculation with intermediate results.""",
            
            """Apply ALGEBRAIC TRANSLATION strategy:
- Convert the entire problem into mathematical expressions/equations
- Assign variables to unknowns (even if obvious)
- Write equation for target quantity
- Solve symbolically first, then substitute numbers
- Show all equation transformations
Example: TotalCost = (Rate1 * Time1) + (Rate2 * Time2)""",
            
            """Apply UNIT-DRIVEN DIMENSIONAL ANALYSIS:
- Focus on unit consistency and propagation
- Treat every number as value + unit (e.g., 30 টাকা/ঘণ্টা)
- Cancel units to derive target unit (e.g., টাকা/ঘণ্টা * ঘণ্টা = টাকা)
- Only perform operations that preserve dimensional validity
- Flag any unit mismatch as error
Output calculation with unit annotations at every step."""
        ]

        # Generate three parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=entity_map) for instr in strategy_instructions]
        )

        # STEP 3: SELF-CRITIQUE & REVISION (VALIDATION LAYER)
        revised_solutions = []
        for i, attempt in enumerate(solution_attempts):
            critique = await self.generate(
                instruction=f"""CRITICALLY REVIEW this solution attempt #{i+1}:
1. Verify all numbers from original problem are used correctly
2. Check unit consistency at every operation (no unitless multiplication)
3. Validate against real-world constraints (no negative items, fractional people unless specified)
4. Confirm arithmetic accuracy (recompute key steps)
5. Ensure final answer matches what was asked for
6. Flag any logical gaps or assumptions not stated in problem
Output detailed critique with specific error locations if found.""",
                context=attempt
            )
            
            # Revise based on self-critique
            revised = await self.revise(
                instruction="""Incorporate the critique to fix errors:
- Correct any arithmetic mistakes
- Add missing steps or constraints
- Adjust units or operations as needed
- If critique finds fundamental flaw, restart solution with corrected approach
- Preserve clear step-by-step reasoning
Output improved solution with changes highlighted.""",
                context=f"Original Attempt:\n{attempt}\n\nCritique:\n{critique}"
            )
            revised_solutions.append(revised)

        # STEP 4: ENSEMBLE SYNTHESIS WITH CONSENSUS VALIDATION
        final_answer = await self.ensemble(
            instruction="""SYNTHESIZE a consensus answer from these three revised solutions:
1. Compare numerical results — do they agree?
2. If disagreement, identify which solution(s) violated constraints or made calculation errors
3. Re-examine original problem to resolve discrepancies
4. Output ONLY the final numerical value that satisfies:
   - Matches at least two solution strategies OR
   - Is validated by dimensional analysis AND chronological simulation
5. If still uncertain, pick the most conservative answer (e.g., higher cost if spending)
6. STRIP all units, explanations, and text — output ONLY the number (integer or decimal)
Example acceptable output: "180" or "255.0" — nothing else.""",
            contexts_list=revised_solutions
        )

        # STEP 5: FINAL EXTRACTION & SANITIZATION (GUARANTEE NUMERIC OUTPUT)
        sanitized_answer = await self.summarize(
            instruction="""EXTRACT ONLY THE FINAL NUMERICAL ANSWER:
- Scan text for numbers (integers or decimals)
- If multiple numbers, select the one matching the problem's requested quantity
- Remove all non-numeric characters (units, commas, text)
- If no clear number, return "0" as fallback
- Output must be parseable as float or int
Example: From "Total cost is 180 টাকা" → "180" """,
            context=final_answer
        )

        # Post-process to ensure clean numeric string
        # Remove any remaining non-numeric except decimal point
        clean_answer = re.sub(r'[^\d.]', '', sanitized_answer)
        
        # Handle edge case: multiple decimal points
        if clean_answer.count('.') > 1:
            # Keep only first decimal point
            parts = clean_answer.split('.')
            clean_answer = parts[0] + '.' + ''.join(parts[1:])
        
        return clean_answer.strip() or "0"