# Workflow ID: mgsmbn_32_0
# Benchmark: mgsmbn
# Data Indices: [11]

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

        # PHASE 1: PARALLEL INTERPRETATION FORK
        # Generate 3 distinct linguistic interpretations to handle ambiguity
        interpretation_instructions = [
            """Analyze the Bengali problem and construct Interpretation A:
            - Prioritize literal reading of quantities and verbs
            - Assume simplest mathematical model first
            - Extract all numbers, units, agents, and actions
            - Map temporal/spatial relationships explicitly
            - Output structured format: Entities, Operations, Constraints""",
            
            """Analyze the Bengali problem and construct Interpretation B:
            - Consider idiomatic or contextual meanings of phrases
            - Look for implied constraints (e.g., 'বাকি' implies subtraction)
            - Identify potential proportionality or rate relationships
            - Flag any ambiguous terms for later validation
            - Output structured format: Entities, Operations, Constraints""",
            
            """Analyze the Bengali problem and construct Interpretation C:
            - Focus on verb aspects and temporal markers
            - Consider compound operations (e.g., percentage then addition)
            - Identify any hidden steps or intermediate calculations
            - Check for unit conversions or scaling factors
            - Output structured format: Entities, Operations, Constraints"""
        ]

        interpretations = await asyncio.gather(
            *[self.generate(instr, "") for instr in interpretation_instructions]
        )

        # PHASE 2: SYMBOLIC MODELING & COMPUTATION
        # Convert each interpretation into executable mathematical model
        modeling_instructions = """Convert the interpretation into a step-by-step mathematical model:
        - Define variables for unknowns
        - Write equations representing relationships
        - Sequence operations chronologically or logically
        - Include unit tracking at each step
        - Compute final numerical result
        - Show all intermediate values
        - Format: Step 1: [operation] = [value] [unit] ... Final Answer: [number]"""

        models = await asyncio.gather(
            *[self.generate(modeling_instructions, interp) for interp in interpretations]
        )

        # PHASE 3: VALIDATION & RECURSIVE REFINEMENT
        # Validate each model and trigger revision if needed
        async def validate_and_refine(model, interp):
            validation = await self.generate(f"""Validate this solution:
            - Check arithmetic accuracy step by step
            - Verify unit consistency throughout
            - Assess contextual plausibility (no negative people, reasonable magnitudes)
            - Cross-reference with original problem entities
            - Flag any assumptions not explicitly stated
            - If any issue found, return 'REVISION_NEEDED: [reason]' else 'VALID'
            """, model)
            
            if "REVISION_NEEDED" in validation:
                # Escalate revision with diagnostic context
                revised = await self.revise(f"""Revise based on validation failure:
                Original Interpretation: {interp}
                Validation Feedback: {validation}
                - Re-examine ambiguous phrases in original problem
                - Re-derive from first principles
                - Consider alternative mathematical models
                - Ensure unit propagation is explicit
                - Recompute with full precision
                """, model)
                return revised
            return model

        validated_models = await asyncio.gather(
            *[validate_and_refine(model, interp) for model, interp in zip(models, interpretations)]
        )

        # PHASE 4: ENSEMBLE SELECTION WITH SCORING
        # Select best solution based on multi-criteria scoring
        final_selection = await self.ensemble(
            """Select the best solution from candidates using this rubric:
            1. Linguistic Fidelity (0-10): How well does it reflect original Bengali text?
            2. Mathematical Correctness (0-10): Are operations and sequence flawless?
            3. Contextual Plausibility (0-10): Does answer make real-world sense?
            Multiply scores. Choose highest. If tie, prefer simpler model.
            Output ONLY the selected solution's final numerical answer as a single number.
            Strip all text, units, explanations. Ensure decimal format if needed.""",
            validated_models
        )

        # PHASE 5: NUMERICAL EXTRACTION & SANITIZATION
        # Ensure output is clean numerical value
        clean_answer = await self.generate(
            """Extract ONLY the numerical answer from the text below.
            - Remove all units, labels, explanations
            - Convert fractions to decimals if present
            - Use '.' for decimal separator
            - If multiple numbers, take the final result
            - Output must be parseable as float()
            """, 
            final_selection
        )

        # Final sanitization using regex to extract number
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', clean_answer)
        if number_match:
            return float(number_match.group(0)) if '.' in number_match.group(0) else int(number_match.group(0))
        else:
            # Fallback: return 0 if extraction fails (shouldn't happen in valid problems)
            return 0