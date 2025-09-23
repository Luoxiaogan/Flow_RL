# Workflow ID: mgsmbn_36_0
# Benchmark: mgsmbn
# Data Indices: [64]

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

        # === STEP 1: PROBLEM CLASSIFICATION & STRUCTURE EXTRACTION ===
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem to extract its mathematical skeleton. 
            Identify and structure the following components:
            1. ENTITIES: All objects, people, or items mentioned (e.g., 'গোলাপ গাছ', 'কাঁটা').
            2. QUANTIFIERS: All numerical values and their associated units or descriptors (e.g., '3টি', '25টি করে').
            3. RELATIONSHIPS: Verbs or phrases indicating mathematical operations (e.g., 'লাগিয়েছেন' → initialization, 'হয়েছে' → result).
            4. SCOPE: Determine what quantifiers like 'প্রতিটি', 'মোট', 'প্রত্যেকটি' refer to.
            5. GOAL: What is the final quantity being asked for?
            6. CONSTRAINTS: Any implicit real-world constraints (e.g., integer-only answers, non-negative quantities).
            Format output as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # === STEP 2: PARALLEL HYPOTHESIS GENERATION ===
        # Generate 4 independent solution attempts using different reasoning strategies
        hypothesis_instructions = [
            """Solve using ALGEBRAIC MODELING:
            - Assign variables to unknowns.
            - Write equations based on relationships.
            - Solve step-by-step with substitution or elimination.
            - Track units at every step.
            - Box final answer as: \\boxed{<number>}""",
            
            """Solve using STEP-BY-STEP NARRATIVE:
            - Break problem into chronological or logical steps.
            - For each step: state operation, show calculation, note intermediate result.
            - Explicitly write units after every number (e.g., '75 গোলাপ').
            - Verify each step against problem text.
            - Box final answer as: \\boxed{<number>}""",
            
            """Solve using UNIT TRACKING & DIMENSIONAL ANALYSIS:
            - Start with given quantities and their units.
            - Multiply/divide to cancel units until reaching target unit.
            - Show unit cancellation explicitly (e.g., '3 গাছ × 25 গোলাপ/গাছ = 75 গোলাপ').
            - Flag any unit mismatches.
            - Box final answer as: \\boxed{<number>}""",
            
            """Solve using VISUAL/SPATIAL REASONING (even if abstract):
            - Imagine the scenario spatially or as a diagram.
            - Use grouping, arrays, or distribution patterns.
            - Translate visual intuition into arithmetic.
            - Example: '3 plants × 25 roses each → 3 rows of 25 → 75 total roses'.
            - Box final answer as: \\boxed{<number>}"""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in hypothesis_instructions]
        )

        # === STEP 3: ENSEMBLE SYNTHESIS WITH VALIDATION ===
        synthesized = await self.ensemble(
            instruction="""Synthesize the best solution from the four hypotheses by:
            1. COMPARING numerical results — if 3/4 agree, favor majority.
            2. CHECKING unit consistency — ensure all steps track units correctly.
            3. VALIDATING against real-world constraints (e.g., no fractional people, non-negative counts).
            4. RECONCILING discrepancies — if answers differ, identify where paths diverged and correct errors.
            5. PRESERVING clearest step-by-step reasoning.
            Output ONLY the final synthesized solution with steps and boxed answer.""",
            contexts_list=hypotheses
        )

        # === STEP 4: VALIDATION FEEDBACK LOOP (max 2 iterations) ===
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""VALIDATE the synthesized solution:
                - Reverse-calculate: Start from answer and work backward to inputs. Do you recover original values?
                - Unit audit: Does every intermediate step have correct, consistent units?
                - Constraint check: Does answer respect real-world limits (integers, positivity)?
                - Linguistic alignment: Does each step correctly map to Bengali phrases (e.g., 'প্রতিটি গোলাপে' → per rose, not per plant)?
                If VALID, output 'VALID: <answer>'. If INVALID, output 'INVALID: <specific error>'.""",
                context=synthesized
            )

            if "VALID:" in validation:
                # Extract answer
                match = re.search(r"VALID:\s*([0-9]+\.?[0-9]*)", validation)
                if match:
                    return match.group(1).strip()
                else:
                    # Fallback: extract from synthesized if validation passed but regex failed
                    match = re.search(r"\\boxed\{([0-9]+\.?[0-9]*)\}", synthesized)
                    if match:
                        return match.group(1).strip()
                    else:
                        # Last resort: return raw synthesized (shouldn't happen)
                        return synthesized.strip()
            else:
                # Revise based on validation feedback
                synthesized = await self.revise(
                    instruction=f"""REVISE based on validation feedback:
                    Validation Result: {validation}
                    - Correct misparsed quantifiers (e.g., ensure 'প্রতিটি' refers to correct noun).
                    - Fix unit mismatches or missing unit tracking.
                    - Adjust for constraint violations (e.g., round to integer if needed).
                    - Re-verify reverse calculation.
                    Output revised solution with \\boxed{{<number>}}.""",
                    context=synthesized
                )

        # Final fallback: return best effort
        match = re.search(r"\\boxed\{([0-9]+\.?[0-9]*)\}", synthesized)
        if match:
            return match.group(1).strip()
        else:
            # Extract any number as last resort
            numbers = re.findall(r"[0-9]+\.?[0-9]*", synthesized)
            return numbers[0] if numbers else "0"