# Workflow ID: mgsmbn_108_0
# Benchmark: mgsmbn
# Data Indices: [132]

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

        # PHASE 1: CONTEXTUAL DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into structured components. Identify and categorize:
1. ENTITIES: All people, objects, or items mentioned (e.g., 'marble bag', 'student', 'car')
2. QUANTITIES: All numerical values with their units (e.g., '20 টাকা', '36 মাস')
3. OPERATIONS: Verbs or phrases indicating mathematical actions (e.g., 'বৃদ্ধি পায়' = increases, 'ভাগ করে' = divides)
4. RELATIONSHIPS: How quantities relate (e.g., 'প্রতি দুমাসে' = every two months, '20% বৃদ্ধি' = 20% increase)
5. CONSTRAINTS: Explicit or implicit limitations (e.g., 'শুধুমাত্র পূর্ণ সংখ্যা' = only whole numbers)
6. TARGET: What is being asked (e.g., '36 মাস পরে দাম' = price after 36 months)

Format as a structured list with clear section headers. Be exhaustive — missing details cause calculation errors.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Using the decomposition, solve the problem with a LITERAL/SEQUENTIAL approach:
- Treat percentage increases as simple additive steps unless specified otherwise
- Calculate step-by-step for each time interval
- Show all intermediate values and unit tracking
- Assume linear progression unless context implies compounding
- Final answer must be a single number""",
            
            """Using the decomposition, solve the problem with a MATHEMATICAL MODELING approach:
- Identify if growth is exponential (compound) or linear (simple)
- Use appropriate formulas (e.g., P = P0 × (1+r)^t for compound growth)
- Define variables explicitly
- Show formula substitution and calculation steps
- Final answer must be a single number""",
            
            """Using the decomposition, solve the problem with a UNIT-BASED SIMULATION approach:
- Break timeline into smallest units (e.g., 2-month intervals)
- Simulate each step chronologically
- Track units and quantities at each stage
- Round only at final step if required
- Final answer must be a single number"""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition) for instr in strategy_instructions]
        )

        # PHASE 3: PARALLEL VALIDATION
        validation_instructions = [
            """Critically validate this solution:
1. Check arithmetic accuracy — recalculate key steps
2. Verify unit consistency throughout
3. Ensure no negative quantities or fractional entities unless allowed
4. Confirm chronological/logical sequence matches problem description
5. Flag any assumption not explicitly stated in problem
6. If errors found, explain precisely what and where
7. End with 'VALID' or 'INVALID: [reason]'""",
        ] * 3  # Same validation for all three strategies

        validations = await asyncio.gather(
            *[self.revise(instruction=instr, context=strat) for instr, strat in zip(validation_instructions, strategies)]
        )

        # PHASE 4: ENSEMBLE DECISION
        ensemble_result = await self.ensemble(
            instruction="""Synthesize the three strategies and their validations to select the best answer:
1. Prioritize mathematically rigorous approaches that match problem semantics
2. Favor solutions with explicit step-by-step justification
3. Eliminate any solution marked 'INVALID' unless error is minor and fixable
4. If multiple valid solutions, choose the one most aligned with elementary math conventions
5. If tie, prefer the solution with clearest unit tracking and intermediate steps
6. Extract ONLY the final numerical answer as a single number — no units, no text""",
            contexts_list=[f"Strategy: {s}\nValidation: {v}" for s, v in zip(strategies, validations)]
        )

        # PHASE 5: FINAL POLISH & VERIFICATION
        final_answer = await self.revise(
            instruction="""Refine this answer to meet strict output requirements:
1. Must be a single numerical value (integer or decimal)
2. No units, no text, no explanations
3. Verify arithmetic one final time using independent calculation
4. If answer contains non-numeric characters, extract only digits and decimal point
5. Round to appropriate decimal places if needed (match problem precision)
6. Output ONLY the number — nothing else""",
            context=ensemble_result
        )

        # Extract pure number using regex (in case any text remains)
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return ensemble result as-is (shouldn't happen with proper validation)
            return final_answer.strip()