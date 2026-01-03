# Workflow ID: mgsmbn_31_0
# Benchmark: mgsmbn
# Data Indices: [105]

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

        # PHASE 1: STRUCTURAL DECOMPOSITION
        problem_structure = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into a structured mathematical model. Follow these steps:
            1. Identify all initial quantities and their associated entities (e.g., "60 elves", "500 taka").
            2. Extract every transformation event in chronological order. For each event:
               - Specify the trigger condition (e.g., "after vomiting")
               - Identify the mathematical operation (add, subtract, multiply, divide, fraction, percentage)
               - Note the operands and affected entities
               - Preserve Bengali phrases that define the operation for traceability
            3. Identify the final query - what is being asked?
            4. Flag any ambiguous phrases or potential misinterpretations.
            5. Output as a numbered timeline with explicit state transitions.
            Example format:
            Step 0: Initial state - [entity: quantity]
            Step 1: [Event description] → Operation: [math] → New state: [entity: quantity]
            Step 2: ...
            Final Query: [question]""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        # Three independent solution strategies
        strategy_instructions = [
            """Solve using CHRONOLOGICAL SIMULATION:
            - Start with initial quantities from the problem.
            - Process each event IN ORDER as described in the narrative.
            - After each operation, explicitly state the new state (e.g., "After 1/3 leave: 60 * 2/3 = 40 elves remain").
            - Maintain running totals for all entities.
            - Never skip intermediate steps - show all arithmetic.
            - If units change (e.g., hours to minutes), show conversion.
            - Final output must directly answer the query.""",
            
            """Solve using ALGEBRAIC MODELING:
            - Define variables for unknowns (e.g., let x = final number of elves).
            - Translate each sentence into an equation or inequality.
            - Preserve Bengali terms as comments for reference.
            - Solve step-by-step, showing all substitutions and simplifications.
            - If the system is underdetermined, state assumptions explicitly.
            - Verify solution satisfies all original conditions.""",
            
            """Solve using UNIT-AWARE ARITHMETIC:
            - Track each entity type separately (elves, taka, hours, etc.).
            - For every operation, verify unit consistency (can't add elves to taka).
            - When fractions/percentages are applied, specify which entity they modify.
            - Maintain dimensional analysis throughout.
            - Explicitly state when an operation reduces/increases a quantity.
            - Final answer must include unit verification."""
        ]

        # Generate initial solutions in parallel
        initial_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_structure) 
              for instr in strategy_instructions]
        )

        # PHASE 3: ADVERSARIAL REVISION
        # Each solution is critiqued and revised
        revised_solutions = []
        for i, solution in enumerate(initial_solutions):
            critique = await self.generate(
                instruction=f"""CRITIQUE THIS SOLUTION:
                - Assume this solution contains exactly ONE critical error.
                - Identify the most likely error type: 
                  1. Arithmetic miscalculation (wrong +, -, ×, ÷)
                  2. Misapplied operation (e.g., used addition instead of multiplication)
                  3. Unit inconsistency (mixed entities)
                  4. Chronological error (wrong event order)
                  5. Fraction/percentage misinterpretation
                  6. Ignored constraint or condition
                - Quote the exact line where the error occurs.
                - Provide the corrected version with detailed justification.
                - Preserve the original strategy's approach while fixing the error.""",
                context=solution
            )
            
            revised = await self.revise(
                instruction="""INCORPORATE THE CRITIQUE:
                - Integrate the identified correction seamlessly.
                - Maintain the original solution's structure and style.
                - Add explicit verification step showing why the correction fixes the error.
                - If no error was found, strengthen the solution with additional validation.""",
                context=f"Original Solution:\n{solution}\n\nCritique:\n{critique}"
            )
            revised_solutions.append(revised)

        # PHASE 4: EXPERT ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""You are three expert mathematicians who solved the same problem independently. 
            Compare your solutions:
            1. If all three answers agree numerically, output that answer.
            2. If there's disagreement:
               - Identify the exact step where solutions diverge
               - Re-examine the original problem's key phrase for that step
               - Vote on the most linguistically and mathematically sound interpretation
               - Justify the winning approach with reference to Bengali text
            3. Output format: 
               "Consensus Answer: [number] 
               Justification: [2-3 sentences explaining why this is correct]""",
            contexts_list=revised_solutions
        )

        # PHASE 5: VALIDATION & EXTRACTION
        validated = await self.generate(
            instruction="""VALIDATE THE FINAL ANSWER:
            - Check against original problem: does it satisfy all stated conditions?
            - Verify dimensional consistency (no negative elves, fractional people unless specified)
            - Ensure all intermediate steps are mathematically sound
            - If any issue is found, propose corrected answer with explanation
            - If valid, output ONLY the numerical answer (no units, no text)""",
            context=f"Final Proposed Answer:\n{final_answer}\n\nOriginal Problem Structure:\n{problem_structure}"
        )

        # Extract clean numerical answer
        clean_answer = await self.summarize(
            instruction="""Extract ONLY the numerical answer from the text below. 
            Rules:
            - If multiple numbers appear, select the one that directly answers the problem's query
            - Remove all units (টাকা, জন, etc.)
            - If decimal, round to 2 decimal places unless exact fraction
            - If fraction, convert to decimal
            - Return ONLY the number, nothing else""",
            context=validated
        )

        # Final sanitization - extract first number from string
        numbers = re.findall(r'-?\d+\.?\d*', clean_answer)
        return numbers[0] if numbers else "0"