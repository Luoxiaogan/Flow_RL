# Workflow ID: mgsmbn_58_0
# Benchmark: mgsmbn
# Data Indices: [176, 125]

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
        import json

        # PHASE 1: PARALLEL EXTRACTION & CLASSIFICATION
        entity_extraction_task = self.generate(
            instruction="""Extract all mathematical entities, relationships, and units from the Bengali problem. Structure output as:
            {
                "entities": [{"name": "...", "role": "..."}],
                "numbers": [{"value": number, "description": "..."}],
                "relationships": [{"subject": "...", "object": "...", "operator": "more/less/times/total", "magnitude": number}],
                "units": [{"unit": "...", "conversion_needed": boolean, "target_unit": "..."}],
                "unknowns": ["..."]
            }
            Be exhaustive. If any relationship is ambiguous, list possible interpretations.""",
            context=""
        )

        problem_classification_task = self.generate(
            instruction="""Classify this problem by type and complexity. Answer in this structure:
            Primary Type: [Sequential / Rate / Proportional / Distribution / Comparison / Multi-entity]
            Secondary Types: [...]
            Complexity Level: [Low / Medium / High]
            Key Operations Needed: [Addition, Subtraction, Unit Conversion, etc.]
            Hidden Steps Likely: [Yes/No]
            Recommended Strategy Count: [1-3]
            Justify each choice with evidence from the problem text.""",
            context=""
        )

        # Await both in parallel
        entity_extraction, classification = await asyncio.gather(entity_extraction_task, problem_classification_task)

        # PHASE 2: STRATEGY GENERATION (FORK)
        strategy_count = 2
        try:
            # Extract recommended strategy count if classification is well-structured
            if "Recommended Strategy Count:" in classification:
                count_line = [line for line in classification.split('\n') if "Recommended Strategy Count:" in line][0]
                strategy_count = int(count_line.split(":")[1].strip())
        except:
            strategy_count = 2

        strategy_instructions = [
            """Develop a DIRECT ARITHMETIC strategy: 
            - Solve step-by-step using only basic operations
            - No algebra, no variables
            - Explicitly show every calculation
            - Handle units by converting early
            Format: Step 1: ... → Result: ...
            Step 2: ... → Result: ...""",
            
            """Develop an ALGEBRAIC MODELING strategy:
            - Define variables for unknowns
            - Set up equations based on relationships
            - Solve systematically
            - Substitute known values last
            Format: Let X = ... Equation: ... Solution: ...""",
            
            """Develop a DIMENSIONAL ANALYSIS strategy:
            - Focus on unit consistency first
            - Convert all quantities to common units
            - Multiply/divide based on 'per', 'each', 'total'
            - Track units at every step
            Format: Quantity A (unit) × Factor = Quantity B (unit) → ..."""
        ]

        strategy_tasks = []
        for i in range(min(strategy_count, len(strategy_instructions))):
            task = self.generate(
                instruction=f"""{strategy_instructions[i]}

                Use this extracted context:
                Entities & Numbers: {entity_extraction}
                Problem Classification: {classification}

                IMPORTANT: If any step requires an assumption, state it explicitly. Show ALL work.""",
                context=""
            )
            strategy_tasks.append(task)

        raw_strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: VALIDATION CASCADE (Parallel per strategy)
        validation_tasks = []
        for strategy in raw_strategies:
            # Revise for errors
            revised = await self.revise(
                instruction="""Critique this solution as a strict math teacher:
                - Check every arithmetic operation
                - Verify unit conversions are applied
                - Ensure all given numbers are used
                - Confirm the unknown is actually solved for
                - Flag any skipped or assumed steps
                If errors found, correct them IN PLACE and mark corrections with [CORRECTED: ...].
                If no errors, append 'VERIFIED: All steps correct.'""",
                context=strategy
            )
            # Summarize into clean solution
            summarized = await self.summarize(
                instruction="""Condense this solution into a clear, step-by-step final version:
                - Remove meta-commentary and revision marks
                - Keep only essential calculations and results
                - End with a boxed final answer: \\boxed{number}
                - Preserve unit labels throughout""",
                context=revised
            )
            validation_tasks.append(summarized)

        validated_strategies = await asyncio.gather(*validation_tasks)

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            1. Compare numerical final answers. If all agree, pick the most clearly reasoned.
            2. If answers disagree, identify the exact step where they diverge.
            3. Re-simulate that step with extra scrutiny: check units, operations, and source numbers.
            4. Select the solution whose assumptions best match the original problem's constraints.
            5. Output ONLY the final numerical answer as a single number (no units, no text).""",
            contexts_list=validated_strategies
        )

        # PHASE 5: SANITY CHECK (Final validation)
        sanity_check = await self.generate(
            instruction=f"""Perform a final sanity check on this answer: {final_answer}
            - Given the problem context, is this magnitude reasonable? (e.g., not negative, not fractional if counting people)
            - Does it match the expected unit type? (e.g., points, feet, taka)
            - Cross-verify with total constraints if applicable (e.g., sum of parts = total)
            If any red flags, output 'RECHECK' followed by reason. Otherwise, output 'VALID: {final_answer}'""",
            context=""
        )

        # Extract final answer (handle potential recheck)
        if "RECHECK" in sanity_check:
            # Fallback: take first strategy's answer
            fallback_answer = validated_strategies[0].split('\\boxed{')[-1].split('}')[0] if '\\boxed{' in validated_strategies[0] else final_answer
            return fallback_answer.strip()
        else:
            # Extract number from 'VALID: ...'
            if "VALID:" in sanity_check:
                final_answer = sanity_check.split("VALID:")[-1].strip()
            return final_answer.strip()