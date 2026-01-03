# Workflow ID: mgsmbn_33_0
# Benchmark: mgsmbn
# Data Indices: [16]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # STEP 1: SEMANTIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break down the Bengali word problem into structured, computable components. For each component, explicitly identify:
            - ENTITIES: Containers, people, or objects with quantities (e.g., "Orange Drink", "Pineapple Drink"). For each, specify: name, initial quantity, unit, and composition (e.g., water fraction).
            - ACTIONS: Chronological events that modify quantities (e.g., "spill 1L", "mix drinks"). Specify: actor, action type, amount, and timing.
            - TARGET: The exact unknown to solve for (e.g., "total water in final 24L mixture").
            - CONSTRAINTS: Implicit real-world rules (e.g., "no negative volume", "fractions sum to 1").
            Output as a list of dictionaries with keys: id, description, dependencies. Ensure units (লিটার, টাকা, etc.) are preserved and fractions are converted to decimals or explicit ratios.""",
            context=""
        )

        # Convert decomposition to string context for downstream use
        decomposition_context = json.dumps(decomposition, ensure_ascii=False, indent=2)

        # STEP 2: PARALLEL SOLUTION TRACKS
        async def generate_algebraic_approach():
            return await self.generate(
                instruction=f"""Using the decomposed structure:
                {decomposition_context}
                
                Develop an ALGEBRAIC SOLUTION:
                - Define variables for unknowns (e.g., W_total = total water).
                - Write equations representing conservation laws (e.g., water_before = water_after).
                - Solve symbolically, showing all steps.
                - Substitute numerical values last.
                - Explicitly state units at every step.
                - Double-check that spillage and mixing events are incorporated chronologically.""",
                context=decomposition_context
            )

        async def generate_simulation_approach():
            return await self.generate(
                instruction=f"""Using the decomposed structure:
                {decomposition_context}
                
                Develop a STEP-BY-STEP SIMULATION:
                - Start with initial states (e.g., "Orange Drink: 10L total, 2/3 water → 6.67L water").
                - Apply each action in sequence (e.g., "Spill 1L: subtract 1L from orange drink, adjust water proportionally").
                - After each step, recalculate all quantities.
                - End with final mixture and sum target value.
                - Track units religiously. Never drop units.
                - Verify that final total volume matches problem statement (e.g., 24L).""",
                context=decomposition_context
            )

        async def generate_programmer_draft():
            return await self.generate(
                instruction=f"""Using the decomposed structure:
                {decomposition_context}
                
                Generate PYTHON CODE to compute the answer:
                - Use variables named after entities (e.g., orange_drink_initial = 10.0).
                - Include comments explaining each step in Bengali/English.
                - Handle fractions as decimals (e.g., 2/3 → 0.6667).
                - Add assertions for constraints (e.g., assert final_volume == 24.0).
                - Print only the final numerical answer.
                - Do NOT use external libraries beyond basic math.""",
                context=decomposition_context
            )

        # Run all three tracks in parallel
        algebraic_sol, simulation_sol, programmer_draft = await asyncio.gather(
            generate_algebraic_approach(),
            generate_simulation_approach(),
            generate_programmer_draft()
        )

        # STEP 3: VALIDATION & REVISION LOOP (max 2 iterations)
        solutions = [algebraic_sol, simulation_sol, programmer_draft]
        validated_solutions = []

        for i, sol in enumerate(solutions):
            current_sol = sol
            for attempt in range(2):  # Max 2 revision attempts
                # Validate for unit consistency and spillage awareness
                validation = await self.generate(
                    instruction=f"""Critically validate this solution:
                    {current_sol}
                    
                    CHECK:
                    1. Are ALL units explicitly tracked and consistent? (e.g., liters not mixed with kg)
                    2. Does it account for EVERY action in decomposition (especially spillage/loss events)?
                    3. Are fractions/percentages applied to correct bases?
                    4. Does the final answer format match the problem's requirement (single number)?
                    If any issue, explain concisely. If perfect, say "VALID".""",
                    context=current_sol
                )

                if "VALID" in validation.upper():
                    validated_solutions.append(current_sol)
                    break
                else:
                    # Revise based on validation feedback
                    current_sol = await self.revise(
                        instruction=f"""Fix the following issues:
                        {validation}
                        
                        Revise the solution to:
                        - Correct unit handling
                        - Incorporate missed actions (e.g., spillage)
                        - Ensure chronological accuracy
                        - Preserve all intermediate steps for traceability""",
                        context=current_sol
                    )
            else:  # If loop completes without break, use last revision
                validated_solutions.append(current_sol)

        # STEP 4: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""Synthesize the three validated solutions:
            - If all three agree numerically, output the consensus value.
            - If two agree, output their value and note the outlier.
            - If all disagree, re-analyze the decomposition focusing on the point of divergence (e.g., fraction interpretation, spillage timing).
            - NEVER average disagreeing answers.
            - Output ONLY the final numerical answer as a single number (integer or decimal).""",
            contexts_list=validated_solutions
        )

        # STEP 5: REAL-WORLD SANITY CHECK
        verified_answer = await self.revise(
            instruction=f"""Perform a final reality check on this answer:
            {final_answer}
            
            - Does it make physical sense? (e.g., water volume cannot exceed total mixture volume)
            - Re-calculate totals manually: if orange drink had X L water and pineapple had Y L, is X+Y ≈ {final_answer}?
            - Is the decimal precision appropriate? (Round to 2 decimals if needed, but preserve exact fractions if integer).
            - If any doubt, recompute using the simplest method (usually simulation).
            Output ONLY the verified numerical answer.""",
            context=final_answer
        )

        return verified_answer