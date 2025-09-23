# Workflow ID: mgsmbn_0_0
# Benchmark: mgsmbn
# Data Indices: [75]

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

        # STEP 1: Problem Decomposition - Extract entities, quantities, operations, and target
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into structured components:
            1. List all named entities (people, objects) and their roles.
            2. Extract all numerical values and what they represent (include units like ঘণ্টা, টাকা, জিনিস).
            3. Identify mathematical operations implied by verbs and phrases (e.g., 'বেশি' = addition/difference, '2/3 অংশ' = multiplication by fraction).
            4. Note any constraints (non-negative, whole numbers, real-world limits).
            5. Explicitly state what is being asked (the unknown).
            Format output as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # STEP 2: Parallel Strategy Generation
        strategy_instructions = [
            """Solve using direct arithmetic translation:
            - Map extracted quantities and operations literally.
            - Perform calculations step by step in chronological or logical order.
            - Show intermediate results.
            - Assume no hidden steps unless implied by context.""",
            
            """Solve using algebraic modeling:
            - Assign variables to unknowns.
            - Form equations based on relationships described.
            - Solve algebraically, showing all steps.
            - Substitute known values at the end.""",
            
            """Solve using unit-aware proportional reasoning:
            - Track units throughout (convert if necessary).
            - Use ratios, proportions, or scaling factors explicitly.
            - Ensure dimensional consistency in every operation.
            - Highlight any unit conversions performed."""
        ]

        strategy_tasks = [
            self.generate(instruction=instr, context=decomposition)
            for instr in strategy_instructions
        ]
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # STEP 3: Adversarial Validation for each strategy
        adversarial_tasks = [
            self.revise(
                instruction=f"""Adversarially critique this solution:
                - Assume it contains an error. What is the MOST LIKELY mistake?
                  (e.g., wrong operation, unit mismatch, sequence error, ignored constraint)
                - If no error is found, explicitly confirm: "NO ERROR DETECTED".
                - Do NOT fix the solution — only diagnose potential flaws.
                - Be specific: quote the suspicious step and explain why it's questionable.""",
                context=strat
            )
            for strat in raw_strategies
        ]
        critiques = await asyncio.gather(*adversarial_tasks)

        # STEP 4: Synthesize with Ensemble
        synthesis = await self.ensemble(
            instruction="""Select or synthesize the best answer:
            - Prefer solutions with no detected errors.
            - If multiple are error-free, choose the one with clearest unit tracking.
            - If all have critiques, select the one with the least severe or most fixable error.
            - If solutions conflict, attempt to merge insights into a coherent answer.
            - Output ONLY the final numerical answer in this format: "ANSWER: <number>"
            - If uncertain, output "REANALYZE" followed by a brief reason.""",
            contexts_list=[f"Strategy:\n{raw_strategies[i]}\n\nCritique:\n{critiques[i]}" for i in range(3)]
        )

        # STEP 5: Iterative Refinement (if needed)
        iteration_count = 0
        current_answer = synthesis
        while "REANALYZE" in current_answer and iteration_count < 2:
            iteration_count += 1
            
            # Extract critique reasons
            error_summary = await self.summarize(
                instruction="Extract all error reasons and constraints mentioned in critiques. List them concisely.",
                context="\n\n".join(critiques)
            )
            
            # Re-generate strategies with error-aware context
            refined_strategy_tasks = [
                self.generate(
                    instruction=f"""Re-solve the problem with heightened caution:
                    Previous errors to avoid: {error_summary}
                    Emphasize: {strategy_instructions[i]}
                    Double-check units, sequence, and constraints.
                    Show all steps explicitly.""",
                    context=decomposition
                )
                for i in range(3)
            ]
            refined_strategies = await asyncio.gather(*refined_strategy_tasks)
            
            # Re-validate
            refined_critiques = await asyncio.gather(*[
                self.revise(
                    instruction="""Critique this refined solution:
                    - Has the previously identified error been fixed?
                    - Are there NEW potential errors?
                    - Confirm or reject solution validity.""",
                    context=strat
                )
                for strat in refined_strategies
            ])
            
            # Re-synthesize
            current_answer = await self.ensemble(
                instruction="""Select the most reliable answer:
                - Solutions that fixed previous errors get priority.
                - Output ONLY "ANSWER: <number>" or "REANALYZE: <reason>".
                - Be conservative — if doubt remains, request reanalysis.""",
                contexts_list=[f"Strategy:\n{refined_strategies[i]}\n\nCritique:\n{refined_critiques[i]}" for i in range(3)]
            )

        # STEP 6: Final Answer Extraction and Validation
        final_answer = await self.revise(
            instruction="""Extract and validate the final numerical answer:
            - If input contains "ANSWER: <number>", extract <number> exactly.
            - Remove all text, units, and explanations — output ONLY the number.
            - If fractional, convert to decimal (max 2 places).
            - Validate: must be non-negative; if problem implies whole entities (people, items), round to integer.
            - If validation fails, output 0 as fallback.
            - NEVER output text — only digits and decimal point.""",
            context=current_answer
        )

        # Clean and return
        # Remove any residual text, keep only number
        match = re.search(r'(-?\d*\.?\d+)', final_answer.replace(',', ''))
        if match:
            cleaned = match.group(1)
            # If integer value, return as int; else float
            if '.' in cleaned:
                return float(cleaned) if float(cleaned) % 1 != 0 else int(float(cleaned))
            else:
                return int(cleaned)
        else:
            return 0  # Fallback