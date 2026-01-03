# Workflow ID: mgsmbn_79_0
# Benchmark: mgsmbn
# Data Indices: [61]

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

        # STEP 1: PARALLEL PROBLEM DECOMPOSITION & STRATEGY CLASSIFICATION
        decomposition_task = self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into its atomic components. Identify:
            - All numerical values and their contextual meaning (e.g., '24 লিটার' is total water, not per person)
            - All entities involved (people, objects, groups)
            - All actions and their chronological or logical sequence
            - All explicit and implicit constraints (e.g., 'অবশিষ্ট' implies subtraction, 'প্রত্যেকে' implies multiplication by count)
            - The ultimate unknown being asked for
            Structure your output clearly with labeled sections. Do not solve yet—only decompose.""",
            context=""
        )

        classification_task = self.generate(
            instruction="""Classify this problem using three independent reasoning lenses:
            LENS 1 (Mathematical Structure): Is this a rate, proportion, distribution, comparison, or sequential operation problem?
            LENS 2 (Linguistic Cues): What Bengali keywords indicate operations? (e.g., 'অংশ' = fraction, 'প্রত্যেকে' = per entity, 'অবশিষ্ট' = remainder)
            LENS 3 (Practical Constraints): What real-world rules apply? (e.g., no negative quantities, discrete vs continuous units)
            For each lens, provide a classification and justification. Then propose the most suitable solution strategy.""",
            context=""
        )

        decomposition, classification = await asyncio.gather(decomposition_task, classification_task)

        # STEP 2: CONDITIONAL ROUTING BASED ON CLASSIFICATION CONSENSUS
        strategy_consensus = await self.ensemble(
            instruction="""Synthesize the three classification lenses into one unified strategy. Resolve conflicts by:
            - Prioritizing mathematical structure when clear
            - Using linguistic cues to disambiguate
            - Applying practical constraints as sanity checks
            Output a single, coherent solution plan with explicit steps and expected operations.""",
            contexts_list=[classification]
        )

        # STEP 3: PARALLEL SOLUTION ATTEMPTS WITH DIVERSE PERSPECTIVES
        solution_perspectives = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using STRICT mathematical formalism:
                - Convert all Bengali phrases to algebraic expressions
                - Define variables for unknowns
                - Show equation setup and solving step-by-step
                - Verify dimensional consistency (units) at each step
                Problem Decomposition: {decomposition}
                Strategy: {strategy_consensus}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using INTUITIVE real-world simulation:
                - Imagine physically acting out the scenario
                - Track quantities chronologically as if you were there
                - Use approximations if helpful, then refine
                - Explain in narrative form with embedded calculations
                Problem Decomposition: {decomposition}
                Strategy: {strategy_consensus}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using UNIT-FOCUSED tracking:
                - Start with initial quantities and units
                - For each action, show unit transformation explicitly
                - Never drop units until final answer
                - Flag any unit inconsistency immediately
                Problem Decomposition: {decomposition}
                Strategy: {strategy_consensus}""",
                context=""
            )
        )

        # STEP 4: ADVERSARIAL VALIDATION - CRITIQUE EACH SOLUTION
        critiques = await asyncio.gather(
            *[self.generate(
                instruction=f"""Act as a SKEPTICAL examiner. Critique this solution:
                - Check arithmetic for errors
                - Verify unit consistency throughout
                - Ensure chronological/logical order matches problem
                - Confirm answer matches question asked
                - Identify any hidden assumptions or leaps
                If error found, specify exactly where and why. If none, state 'VALID'.
                Solution to critique: {sol}""",
                context=""
            ) for sol in solution_perspectives]
        )

        # STEP 5: REVISE SOLUTIONS BASED ON CRITIQUES
        revised_solutions = []
        for i, (sol, crit) in enumerate(zip(solution_perspectives, critiques)):
            if "VALID" not in crit.upper() or "ERROR" in crit.upper() or "INCORRECT" in crit.upper():
                revised = await self.revise(
                    instruction=f"""Revise this solution based on the critique:
                    Original Solution: {sol}
                    Critique: {crit}
                    - Fix all identified errors
                    - Add missing steps or justifications
                    - Preserve correct parts
                    - Re-verify units and logic
                    Output the complete corrected solution.""",
                    context=sol
                )
                revised_solutions.append(revised)
            else:
                revised_solutions.append(sol)  # No revision needed

        # STEP 6: FINAL ENSEMBLE SYNTHESIS WITH CONSTRAINT VALIDATION
        final_answer = await self.ensemble(
            instruction="""Synthesize the revised solutions into one final answer. Apply these rules:
            1. If all solutions agree numerically, output that number.
            2. If they disagree, choose the one with the most rigorous unit tracking and step-by-step justification.
            3. Apply final sanity checks: 
               - Does the answer make sense in context? (e.g., no negative water, no fractional people if implied)
               - Is the unit correct and consistent?
               - Does it match the problem's requested format (integer or decimal)?
            4. Extract ONLY the final numerical value as a string. No units. No explanation.
            Example: If answer is 10 liters, output "10". If 15.5 kg, output "15.5".""",
            contexts_list=revised_solutions
        )

        # STEP 7: EXTRACTION AND CLEANING (in case ensemble includes text)
        # Use regex to extract first number (integer or decimal) from the string
        match = re.search(r'(-?\d+\.?\d*)', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return final_answer.strip()