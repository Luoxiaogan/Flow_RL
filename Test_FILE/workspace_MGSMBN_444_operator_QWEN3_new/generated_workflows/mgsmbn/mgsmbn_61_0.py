# Workflow ID: mgsmbn_61_0
# Benchmark: mgsmbn
# Data Indices: [5, 96]

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

        # PHASE 1: LINGUISTIC & STRUCTURAL DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into its mathematical components. 
            Extract and explicitly list:
            1. All numerical values with their units (টাকা, ঘণ্টা, পৃষ্ঠা, etc.) and contextual meaning
            2. The unknown being asked for (clearly state what needs to be calculated)
            3. Relationships between quantities (ratios, rates, proportions, sequences)
            4. Problem type classification with confidence (rate, distribution, comparison, etc.)
            5. Any constraints or real-world limitations (non-negative, integer-only, etc.)
            Format as a structured markdown list with clear section headers. Be exhaustive.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        strategy_instructions = [
            """Solve by CHRONOLOGICAL SIMULATION: 
            - Imagine enacting the scenario step by step in real time
            - Break into discrete, ordered operations matching the problem's narrative flow
            - Show intermediate values with units at each step
            - Never use algebraic variables; only concrete calculations
            - Example: 'First, calculate regular pay: 40 hours × $10/hour = $400. Then calculate overtime: 5 hours × $12/hour = $60...'""",
            
            """Solve by ALGEBRAIC ABSTRACTION:
            - Define variables for unknowns and key quantities
            - Write equations representing relationships
            - Solve symbolically before substituting numbers
            - Show equation transformations step by step
            - Example: 'Let T = total earnings. T = 40×10 + (45-40)×(10×1.2). Therefore T = 400 + 5×12 = 460'""",
            
            """Solve by UNIT ANALYSIS & DIMENSIONAL REASONING:
            - Track units at every calculation step (টাকা, ঘণ্টা, পৃষ্ঠা, etc.)
            - Verify dimensional consistency: hours × rate/hour = earnings
            - Reject any step where units don't align
            - Convert units explicitly when needed
            - Example: '45 hours total - 40 regular hours = 5 overtime hours. Overtime rate: $10/hour × 1.2 = $12/hour. Earnings: 40h×$10/h + 5h×$12/h = $460'"""
        ]

        # Generate three parallel solution attempts
        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition) 
              for instr in strategy_instructions]
        )

        # PHASE 3: SYNTHESIS & VALIDATION
        final_answer = await self.ensemble(
            instruction="""Synthesize these three solution attempts into one definitive answer:
            1. Compare numerical results - do they agree?
            2. Evaluate methodological soundness of each approach
            3. Check for unit consistency and real-world plausibility
            4. If all agree, return the consensus value
            5. If two agree and one differs, return majority and note discrepancy
            6. If all differ, trigger fallback: re-express problem from first principles
            7. Final output MUST be ONLY the numerical answer (integer or decimal) with no units or explanation""",
            contexts_list=strategy_attempts
        )

        # EXTRACTION & SANITIZATION (ensure pure numerical output)
        # Extract first number from the ensemble result
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer)
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: attempt to extract from original attempts if ensemble failed
            for attempt in strategy_attempts:
                match = re.search(r'[-+]?\d*\.\d+|\d+', attempt)
                if match:
                    return float(match.group()) if '.' in match.group() else int(match.group())
            # Ultimate fallback: return 0 (should never happen)
            return 0