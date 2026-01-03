# Workflow ID: mgsmbn_30_0
# Benchmark: mgsmbn
# Data Indices: [47, 63]

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

        # PHASE 1: SEMANTIC DECOMPOSITION & CLASSIFICATION
        decomposition = await self.generate(
            instruction="""Perform a comprehensive semantic decomposition of this Bengali math word problem. Extract and categorize the following components with high precision:

1. ENTITIES: List all people, objects, or agents mentioned (e.g., 'সোফিয়া', 'গ্রেস', 'গাড়ি').
2. QUANTITIES: Extract every numerical value with its associated unit and description (e.g., '100 মাইল', '4 গ্যালন', '125 পাউন্ড').
3. RELATIONSHIPS: Describe how quantities relate (e.g., 'Alex's weight is 4 times Grace's minus 2', '100 miles consumed 4 gallons').
4. TARGET: Explicitly state what is being asked (e.g., 'total distance on full tank', 'combined weight').
5. CONSTRAINTS: Note any implicit or explicit constraints (e.g., 'tank capacity is fixed', 'weights must be positive').
6. UNITS: List all units involved and whether conversions are needed.
7. PROBLEM TYPE: Classify as one of: Rate, Proportional, Multi-step Arithmetic, Algebraic, or Comparison.

Format your response as a structured markdown list with clear section headers. Be exhaustive and precise.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        strategy_instructions = [
            """You are a Unit Rate Specialist. Solve this problem by:
- Identifying the base rate (e.g., miles per gallon, cost per item)
- Calculating it from given partial quantities
- Scaling it to the target condition
- Showing all unit conversions explicitly
- Verifying dimensional consistency at each step
Present your solution as a numbered sequence of calculations with brief justifications.""",
            
            """You are an Algebraic Modeler. Solve this problem by:
- Assigning variables to unknown quantities
- Writing equations based on stated relationships
- Solving the system step by step
- Substituting known values
- Checking for constraint violations
Show your work as algebraic expressions followed by numerical substitution.""",
            
            """You are a Chronological Simulator. Solve this problem by:
- Walking through events in the order described
- Updating quantities after each action
- Tracking units and conversions
- Handling remainders or partial quantities
- Stopping when the target is reached
Present as a timeline with state changes at each step."""
        ]

        strategy_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition) for instr in strategy_instructions]
        )

        # PHASE 3: SYNTHESIS & VERIFICATION
        audited_solution = await self.ensemble(
            instruction="""You are a Mathematical Auditor. Your task is to:

1. COMPARE the three solution approaches provided. Look for:
   - Numerical agreement or disagreement
   - Differences in intermediate steps
   - Handling of units and conversions
   - Adherence to constraints
   - Logical completeness

2. DIAGNOSE any discrepancies. Trace back to where strategies diverged and why.

3. SYNTHESIZE a final answer by:
   - Selecting the most robust solution if they agree
   - Reconciling differences if they disagree
   - Adding missing steps or corrections as needed
   - Ensuring real-world plausibility (no negative distances, fractional people, etc.)

4. OUTPUT ONLY THE FINAL NUMERICAL ANSWER as a single number (integer or decimal) with no units or explanation.
   Example: 300 or 623.5""",
            contexts_list=strategy_solutions
        )

        # PHASE 4: ADVERSARIAL VALIDATION (Iterative Refinement)
        final_answer = await self.revise(
            instruction="""You are a Skeptical Mathematician. Assume the provided solution is WRONG. Your task:

1. CRITICALLY EXAMINE every step of the solution. Look for:
   - Arithmetic errors (wrong operations, miscalculations)
   - Unit mismatches or missing conversions
   - Logical gaps (skipped steps, unjustified assumptions)
   - Constraint violations (negative quantities, impossible values)

2. If you find an error:
   - Explain exactly what is wrong
   - Provide the corrected calculation
   - Output the corrected final number

3. If you find no error:
   - Reaffirm the solution with additional validation
   - Output the same number

OUTPUT ONLY THE FINAL NUMERICAL ANSWER as a single number (integer or decimal). No explanations, no units.
Example: 300 or 623.5""",
            context=audited_solution
        )

        # Extract pure number from final answer (defensive parsing)
        # Handle cases where model might add text despite instructions
        match = re.search(r'[-+]?\d*\.?\d+', final_answer)
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return as-is if no number found (let upstream handle)
            return final_answer