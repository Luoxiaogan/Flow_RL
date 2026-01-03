# Workflow ID: mgsmbn_116_0
# Benchmark: mgsmbn
# Data Indices: [60]

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

        # PHASE 1: SEMANTIC DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into structured components. Extract:
            1. All numerical values with their semantic roles (e.g., '100' → 'original cost in USD')
            2. Entities involved (people, objects, places) and their relationships
            3. Mathematical operations implied by verbs/nouns (e.g., 'ছাড়' → discount → multiplication by (1 - rate))
            4. Temporal or causal sequence markers ('then', 'after', 'because')
            5. Units of measurement and conversion requirements
            6. Constraints (e.g., 'must be integer', 'positive only', 'less than 100')
            7. The unknown being asked for
            Format as a structured outline with clear section headers. Be exhaustive.""",
            context=""
        )

        # PHASE 2: STRATEGY CLASSIFICATION
        strategy_classification = await self.generate(
            instruction="""Based on the decomposition, classify this problem into exactly ONE primary type:
            - Proportional (percentages, ratios, scaling)
            - Sequential (step-by-step state changes)
            - Distribution (sharing, dividing, remainders)
            - Rate-Based (speed, work rate, unit price)
            - Comparison (differences, 'how many more/less')
            Justify your classification in one sentence referencing specific elements from the decomposition.
            Output format: "CLASSIFICATION: [Type] | JUSTIFICATION: [sentence]" """,
            context=decomposition
        )

        # Extract classification for branching
        primary_strategy = "Proportional"  # default fallback
        if "CLASSIFICATION:" in strategy_classification:
            primary_strategy = strategy_classification.split("CLASSIFICATION:")[1].split("|")[0].strip()

        # Define strategy-specific instructions
        strategy_instructions = {
            "Proportional": "Solve as a proportional reasoning problem. Identify base value and multiplier (e.g., discount rate, ratio). Show calculation of scaled value. Verify percentage logic (e.g., 30% off means multiply by 0.7).",
            "Sequential": "Solve as a sequential state problem. Track changes step by step in chronological order. Show state after each operation. Verify order of operations matches problem narrative.",
            "Distribution": "Solve as a distribution problem. Identify total quantity and number of recipients. Calculate per-unit share. Handle remainders appropriately. Verify divisibility constraints.",
            "Rate-Based": "Solve as a rate problem. Identify rate, time, and quantity. Use formula: quantity = rate × time. Verify unit consistency (e.g., km/h × h = km).",
            "Comparison": "Solve as a comparison problem. Identify compared entities and difference operator ('more than', 'less than'). Set up equation: A = B + difference. Verify directionality of comparison."
        }

        # Select 2-3 most plausible strategies (primary + fallbacks)
        fallback_strategies = {
            "Proportional": ["Sequential", "Comparison"],
            "Sequential": ["Proportional", "Rate-Based"],
            "Distribution": ["Proportional", "Comparison"],
            "Rate-Based": ["Sequential", "Proportional"],
            "Comparison": ["Proportional", "Sequential"]
        }
        
        selected_strategies = [primary_strategy] + fallback_strategies.get(primary_strategy, [])[:2]

        # PHASE 3: PARALLEL STRATEGY SIMULATION
        strategy_tasks = []
        for strategy in selected_strategies:
            instruction = f"""{strategy_instructions.get(strategy, 'Solve using general mathematical reasoning.')}
            Use the problem decomposition as your guide.
            Show ALL intermediate steps with clear labels.
            Track units throughout.
            Box your final numerical answer at the end.
            If any step seems ambiguous, state your assumption explicitly."""
            
            task = self.generate(instruction=instruction, context=decomposition)
            strategy_tasks.append(task)

        # Execute strategies in parallel
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # PHASE 4: ENSEMBLE VALIDATION & SELECTION
        final_answer = await self.ensemble(
            instruction="""You are given multiple candidate solutions to the same Bengali math problem.
            For each candidate:
            1. Verify that intermediate steps logically follow from the problem text
            2. Check unit consistency throughout the calculation
            3. Assess plausibility of final answer (e.g., positive, reasonable magnitude)
            4. Cross-validate against other candidates — do any agree?
            Select the candidate that best satisfies all criteria. If multiple are valid and agree, pick any.
            If all have flaws, synthesize a new answer by combining valid steps from each.
            Output ONLY the final numerical answer as a single number (integer or decimal).""",
            contexts_list=strategy_solutions
        )

        # PHASE 5: REALITY CHECK & FINAL REVISION
        # Check if answer should be integer (e.g., count of people, items)
        reality_check = await self.generate(
            instruction="""Based on the original problem, determine if the answer MUST be an integer (e.g., number of children, whole items, discrete objects).
            If yes, and the current answer is fractional, it must be rounded to nearest integer.
            If no, leave as is.
            Output format: "REQUIRES_INTEGER: yes/no | REASON: [brief justification]" """,
            context=f"Problem: {self.problem_text}\n\nProposed Answer: {final_answer}"
        )

        if "REQUIRES_INTEGER: yes" in reality_check and re.search(r'\.\d+', str(final_answer)):
            # Round to nearest integer
            final_answer = await self.revise(
                instruction="""The problem requires an integer answer (e.g., count of discrete entities), but the current answer is fractional.
                Round to the nearest integer. Justify briefly.
                Output ONLY the revised numerical answer.""",
                context=str(final_answer)
            )

        # Final output must be clean numerical value
        # Extract number from string (handles cases where ensemble outputs text)
        match = re.search(r'[-+]?\d*\.\d+|\d+', str(final_answer))
        if match:
            return float(match.group()) if '.' in match.group() else int(match.group())
        else:
            # Fallback: return 0 if no number found (shouldn't happen)
            return 0