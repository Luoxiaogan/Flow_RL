# Workflow ID: mgsmbn_13_0
# Benchmark: mgsmbn
# Data Indices: [160, 68]

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

        # PHASE 1: Problem Classification and Structural Decomposition
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this Bengali math word problem. Your task:

1. CLASSIFY the problem type using these categories:
   - Sequential Operations (multiple steps in time/order)
   - Rate/Proportion (speed, unit price, scaling, fractions, percentages)
   - Distribution/Division (sharing, remainders, equal parts)
   - Comparison/Difference (how many more/less, relative quantities)
   - Multi-entity Tracking (multiple people/objects with different values)

2. EXTRACT all numerical values and their contextual meaning:
   - What does each number represent? (e.g., "5 buckets", "0.75 bags per guest")
   - Are there implicit conversions? (e.g., "1/4 didn't attend" → 75% attendance)

3. IDENTIFY the unknown: What exactly are we solving for?

4. DETECT hidden steps or assumptions:
   - Are there unstated operations? (e.g., sum before multiply)
   - Are units consistent? Do conversions need to happen?

5. ASSESS complexity level:
   - Low: Direct calculation (1-2 steps)
   - Medium: Requires inference or unit conversion (2-3 steps)
   - High: Multi-entity or conditional logic (3+ steps)

Output in this exact JSON-like structure (without actual JSON syntax):
TYPE: [classification]
NUMBERS: [list with descriptions]
UNKNOWN: [description]
HIDDEN_STEPS: [list or "None"]
COMPLEXITY: [Low/Medium/High]""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation (Diamond Pattern)
        strategy_instructions = [
            """You are a DIRECT CALCULATION expert. Ignore narrative — focus only on numbers and explicit operations.
Steps:
1. List all numbers in order of appearance.
2. Identify explicit operators (+, -, ×, ÷) or implied ones (e.g., 'each' implies multiplication).
3. Apply operations in narrative order unless parentheses or precedence rules override.
4. Show raw calculation string before computing.
5. Compute result. Keep full precision.
Output format: "DIRECT: [calculation string] = [result]" """,

            """You are a PROPORTIONAL REASONING expert. Assume everything is a ratio, fraction, or percentage.
Steps:
1. Identify base quantity and scaling factor.
2. Convert fractions/percentages to decimals.
3. Apply proportional adjustment (e.g., if 1/4 absent, multiply by 0.75).
4. Check if answer should be integer (e.g., people, bags) — round only if context demands.
Output format: "PROPORTION: [base] × [factor] = [result]" """,

            """You are a CHRONOLOGICAL TRACKER. Model the problem as a sequence of events over time.
Steps:
1. Break problem into time-ordered steps (morning/evening, before/after, day1/day2).
2. Track cumulative changes at each step.
3. Sum or aggregate final state.
4. Explicitly state intermediate totals.
Output format: "CHRONO: Step1: [value], Step2: [value], Total: [result]" """,

            """You are an ALGEBRAIC MODELER. Define variables and solve equations.
Steps:
1. Let X = unknown quantity.
2. Write equation based on relationships in text.
3. Solve step-by-step.
4. Verify solution satisfies all conditions.
Output format: "ALGEBRA: Equation: [equation], Solution: X = [result]" """
        ]

        # Generate parallel strategies
        strategy_tasks = [
            self.generate(instruction=instr, context=problem_analysis)
            for instr in strategy_instructions
        ]
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Adversarial Validation & Revision
        validated_strategies = []
        for strategy in raw_strategies:
            validated = await self.revise(
                instruction=f"""CRITIQUE AND REVISE this solution:

1. UNIT CHECK: Are units consistent? (e.g., liters, bags, টাকা) If not, convert.
2. ORDER CHECK: Does operation order match problem logic? (e.g., sum before multiply)
3. CONTEXT CHECK: Is result plausible? (No negative people, fractional items only if allowed)
4. HIDDEN STEP CHECK: Did you miss any implied operations from the original problem?
5. PRECISION CHECK: Decimal places appropriate? Round only if context requires.

If any error found, CORRECT it and explain the fix.
If no error, output "VALID: [original strategy]" """,
                context=strategy
            )
            validated_strategies.append(validated)

        # PHASE 4: Ensemble Synthesis with Reasoning Quality Weighting
        final_answer = await self.ensemble(
            instruction="""SELECT OR SYNTHESIZE the best final answer:

1. Compare all validated strategies.
2. Prefer solutions that:
   - Explicitly address hidden steps from problem analysis
   - Maintain unit consistency
   - Match the classified problem type (e.g., use proportional for rate problems)
   - Show clear, step-by-step reasoning
3. If multiple answers agree numerically, choose the one with the clearest justification.
4. If answers conflict, synthesize by:
   - Identifying which strategy best fits the problem's linguistic structure
   - Applying Occam's razor — simplest valid explanation wins
5. OUTPUT ONLY THE NUMERICAL VALUE. No units, no text.

Example outputs: "55", "24.0", "17.5" """,
            contexts_list=validated_strategies
        )

        # PHASE 5: Final Sanitization (Ensure pure numeric output)
        sanitized = await self.generate(
            instruction="""Extract ONLY the numerical answer from the text below. Rules:
- Remove all units (টাকা, liters, bags, etc.)
- Remove all explanatory text
- If decimal, keep up to 2 places (e.g., 24.00 → 24, 17.50 → 17.5)
- If integer, output as integer (no .0)
- If multiple numbers, pick the one that matches the problem's unknown

Output format: ONLY the number, nothing else.""",
            context=final_answer
        )

        # Clean extraction using regex as fallback
        match = re.search(r'(-?\d+\.?\d*)', sanitized)
        if match:
            answer_str = match.group(1)
            # Convert to int if whole number, else float
            if '.' in answer_str:
                answer = float(answer_str)
                if answer.is_integer():
                    return int(answer)
                return answer
            else:
                return int(answer_str)
        else:
            # Fallback: return raw sanitized if regex fails
            return sanitized.strip()