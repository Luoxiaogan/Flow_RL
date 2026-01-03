# Workflow ID: mgsmbn_49_0
# Benchmark: mgsmbn
# Data Indices: [148]

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

        # PHASE 1: Narrative Reconstruction with Ambiguity Flagging
        narrative = await self.generate(
            instruction="""Perform deep narrative decomposition of the Bengali word problem. 
            Extract and structure the following for EVERY event in chronological order:
            1. ACTOR: Who or what is performing the action?
            2. ACTION: What is happening? (give, take, move, split, etc.)
            3. QUANTITY: What numerical value is involved? Include units (টাকা, জিনিস, ঘণ্টা, etc.)
            4. MODIFIERS: Any qualifiers ('half', 'twice', 'more than', 'less than', 'remaining')
            5. DEPENDENCIES: Does this step rely on a previous calculation?
            6. AMBIGUITIES: Flag ANY step where multiple mathematical interpretations are possible.
            7. CONSTRAINTS: Note real-world constraints (no negative people, whole items only, etc.)
            
            Format as numbered list with clear section headers. Be exhaustive - do not skip steps.
            Example format:
            Event 1:
            - Actor: Rina
            - Action: gave apples
            - Quantity: 3 apples
            - Modifiers: none
            - Dependencies: none
            - Ambiguities: none
            - Constraints: apples must be non-negative integer""",
            context=""
        )

        # PHASE 2: Mathematical Modeling with Parallel Interpretation Handling
        # Check if ambiguities were flagged
        has_ambiguity = "ambiguities" in narrative.lower() and ("multiple" in narrative.lower() or "possible" in narrative.lower())

        if has_ambiguity:
            # Generate multiple interpretations in parallel
            interpretations = await asyncio.gather(
                self.generate(
                    instruction=f"""Based on the narrative: {narrative}
                    Generate Interpretation A: Choose the most literal mathematical interpretation.
                    Map each event to a mathematical operation. Define variables if needed.
                    Show the complete sequence of calculations step by step.
                    Format: 'Step 1: [operation] → [result]'""",
                    context=narrative
                ),
                self.generate(
                    instruction=f"""Based on the narrative: {narrative}
                    Generate Interpretation B: Choose the most contextually reasonable interpretation.
                    Consider real-world constraints and typical problem patterns.
                    Map each event to a mathematical operation. Define variables if needed.
                    Show the complete sequence of calculations step by step.
                    Format: 'Step 1: [operation] → [result]'""",
                    context=narrative
                ),
                self.generate(
                    instruction=f"""Based on the narrative: {narrative}
                    Generate Interpretation C: Choose the interpretation that preserves integer results.
                    Prioritize interpretations that avoid fractions where context suggests whole units.
                    Map each event to a mathematical operation. Define variables if needed.
                    Show the complete sequence of calculations step by step.
                    Format: 'Step 1: [operation] → [result]'""",
                    context=narrative
                )
            )
            
            # Validate each interpretation
            validations = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Validate this solution: {interp}
                    Check for:
                    1. Mathematical correctness (arithmetic errors)
                    2. Unit consistency throughout
                    3. Constraint satisfaction (no negative quantities where impossible, integer results where required)
                    4. Alignment with narrative events
                    Return 'VALID' if all checks pass, otherwise list specific errors.""",
                    context=interp
                ) for interp in interpretations]
            )
            
            # Filter valid interpretations
            valid_interps = [interp for interp, val in zip(interpretations, validations) if "VALID" in val.upper()]
            
            if len(valid_interps) == 0:
                # All failed - use ensemble to synthesize best attempt
                final_interp = await self.ensemble(
                    instruction="""None of the interpretations fully satisfy constraints.
                    Synthesize a new solution by combining the most valid elements from each attempt.
                    Prioritize: 1) Mathematical correctness, 2) Constraint satisfaction, 3) Narrative alignment.
                    Output only the final numerical answer after 'FINAL ANSWER:'""",
                    contexts_list=interpretations
                )
            elif len(valid_interps) == 1:
                final_interp = valid_interps[0]
            else:
                # Multiple valid - choose most contextually appropriate
                final_interp = await self.ensemble(
                    instruction="""Multiple valid interpretations exist. Select the one that:
                    1. Best matches typical elementary math problem patterns
                    2. Is most educationally appropriate for grade school level
                    3. Has the cleanest, most straightforward calculation path
                    Output only the selected interpretation.""",
                    contexts_list=valid_interps
                )
        else:
            # No ambiguity - single interpretation path
            final_interp = await self.generate(
                instruction=f"""Based on the narrative: {narrative}
                Generate the mathematical solution:
                - Map each event to a mathematical operation
                - Show complete sequence of calculations step by step
                - Track units throughout
                - Verify against constraints
                Format: 'Step 1: [operation] → [result with units]'""",
                context=narrative
            )

        # PHASE 3: Core Entity Summarization (Prune Irrelevant Elements)
        core_model = await self.summarize(
            instruction="""From the mathematical solution, extract ONLY the core entities and operations needed for the final answer.
            Remove any intermediate steps or entities that don't directly contribute to the final calculation.
            Justify why each remaining element is essential.
            This should be a minimal, sufficient mathematical model.""",
            context=final_interp
        )

        # PHASE 4: Final Calculation and Answer Extraction
        final_answer = await self.revise(
            instruction=f"""From this mathematical model: {core_model}
            Perform the final calculation to get a single numerical answer.
            - Show all arithmetic steps
            - Convert any fractions/decimals to final decimal form
            - Round appropriately based on context (usually to nearest integer unless decimals specified)
            - Verify unit consistency one final time
            - Output ONLY the numerical value with no units, labels, or explanations.
            Example: If answer is 25.0, output '25'""",
            context=core_model
        )

        # PHASE 5: Final Validation and Cleanup
        # Extract just the number using regex to ensure clean output
        match = re.search(r'[-+]?\d*\.?\d+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return final_answer.strip()