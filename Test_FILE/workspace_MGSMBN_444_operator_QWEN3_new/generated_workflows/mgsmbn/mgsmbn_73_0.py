# Workflow ID: mgsmbn_73_0
# Benchmark: mgsmbn
# Data Indices: [163, 199]

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

        # === STEP 1: PARALLEL EXTRACTION (Diamond Pattern Fork) ===
        literal_extraction = self.generate(
            instruction="""Perform LITERAL EXTRACTION:
            - Identify every explicit number and its associated noun (e.g., "5 cookies", "8 slices")
            - List all named entities (people, objects, meals, days)
            - Extract direct actions (e.g., "ate", "used", "divided")
            - Do NOT infer relationships. Only extract what is explicitly stated.
            Format as bullet points with clear labels.""",
            context=""
        )
        
        relational_extraction = self.generate(
            instruction="""Perform RELATIONAL EXTRACTION:
            - Identify all comparative phrases ("more than", "less than", "times as many")
            - Extract multipliers, ratios, fractions, percentages
            - Infer implicit operations (e.g., "one more than" implies +1)
            - Map relationships between entities (who vs whom, what vs what)
            Format as structured comparisons with mathematical operators.""",
            context=""
        )
        
        temporal_extraction = self.generate(
            instruction="""Perform TEMPORAL/STRUCTURAL EXTRACTION:
            - Identify time units (daily, weekly, per meal, on Monday)
            - Extract aggregation scope (total for week, sum across meals)
            - Note sequence of events (first...then...finally)
            - Identify grouping (per sandwich, per person, per day)
            Format as timeline or grouped structure with scopes.""",
            context=""
        )

        # Execute parallel extractions
        extractions = await asyncio.gather(literal_extraction, relational_extraction, temporal_extraction)
        
        # === STEP 2: ENSEMBLE SYNTHESIS ===
        synthesized_model = await self.ensemble(
            instruction="""SYNTHESIZE INTO UNIFIED PROBLEM MODEL:
            You have three extraction perspectives. Combine them into one coherent representation.
            Rules:
            1. Prioritize relational and temporal consistency over literal if conflict exists.
            2. Resolve pronoun references (e.g., "he" → "Carl").
            3. Explicitly state all mathematical operations needed.
            4. Flag any remaining ambiguity with [AMBIGUITY: ...].
            5. Structure output as:
               Entities: {list}
               Quantities: {list with units}
               Relationships: {mathematical expressions}
               Constraints: {real-world limits}
               Target: {what to solve for}""",
            contexts_list=extractions
        )

        # === STEP 3: PROBLEM CLASSIFICATION (Conditional Branch Trigger) ===
        classification = await self.generate(
            instruction="""CLASSIFY PROBLEM TYPE:
            Based on the synthesized model, classify into primary type:
            - Sequential Operations (step-by-step changes over time)
            - Rate/Proportion (speed, unit price, ratios, scaling)
            - Distribution/Division (sharing, remainders, equal parts)
            - Comparison/Difference (how many more/less, delta calculations)
            - Multi-entity Tracking (multiple actors with different quantities)
            
            If hybrid, identify primary (80% weight) and secondary (20% weight).
            Justify classification with 2-3 sentence reasoning referencing the model.
            Output format: "TYPE: [Primary] | SECONDARY: [Secondary if any] | REASON: ..." """,
            context=synthesized_model
        )

        # === STEP 4: STRATEGY-BASED SOLUTION GENERATION ===
        solution_strategy = ""
        if "Sequential Operations" in classification or "Multi-entity Tracking" in classification:
            solution_strategy = """SOLVE AS SEQUENTIAL/MULTI-ENTITY:
            - Create timeline or entity table
            - Compute step-by-step changes
            - Aggregate totals per entity/time
            - Show intermediate sums
            - Maintain unit consistency throughout"""
        elif "Rate/Proportion" in classification:
            solution_strategy = """SOLVE AS RATE/PROPORTION:
            - Identify base rate (e.g., per hour, per item)
            - Apply scaling factors
            - Use cross-multiplication if ratios
            - Convert units if necessary
            - Show dimensional analysis"""
        elif "Distribution/Division" in classification:
            solution_strategy = """SOLVE AS DISTRIBUTION:
            - Identify total quantity and number of recipients
            - Compute quotient and remainder
            - Handle fractional parts if allowed
            - Apply constraints (e.g., no partial people)"""
        elif "Comparison/Difference" in classification:
            solution_strategy = """SOLVE AS COMPARISON:
            - Compute base quantities for each entity
            - Apply multipliers/comparatives
            - Calculate delta (difference)
            - Convert units if final answer requires (e.g., calories)"""
        else:
            solution_strategy = """GENERAL SOLVE:
            - Break into subproblems
            - Solve each mathematically
            - Combine results
            - Verify against constraints"""

        initial_solution = await self.generate(
            instruction=f"""{solution_strategy}
            
            Using the synthesized problem model:
            {synthesized_model}
            
            Show ALL steps clearly. Box final answer as: \\boxed{{answer}}.
            Include unit tracking at each step. Double-check arithmetic.""",
            context=synthesized_model
        )

        # === STEP 5: VALIDATION LOOP (Self-Correcting) ===
        current_solution = initial_solution
        for attempt in range(3):  # Max 3 attempts
            validation = await self.generate(
                instruction=f"""VALIDATE THIS SOLUTION:
                Check for:
                1. All extracted values from model used? (cross-check with: {synthesized_model})
                2. Order of operations matches problem logic?
                3. Units consistent and converted properly?
                4. Final answer plausible? (non-negative, integer if required, reasonable magnitude)
                5. Matches target from model?
                
                If any error, state: "ERROR: [description]" and suggest fix.
                If perfect, state: "VALIDATED: Ready for extraction."
                Be brutally honest. Do not affirm if uncertain.""",
                context=current_solution
            )
            
            if "ERROR" in validation or "error" in validation:
                current_solution = await self.revise(
                    instruction=f"""REVISE BASED ON VALIDATION:
                    Validation feedback: {validation}
                    
                    Fix all identified errors. Maintain step-by-step clarity.
                    Re-verify arithmetic and unit consistency.
                    Keep \\boxed{{answer}} format for final answer.""",
                    context=current_solution
                )
            else:
                break  # Exit loop if validated

        # === STEP 6: FINAL ANSWER EXTRACTION ===
        final_answer = await self.summarize(
            instruction="""EXTRACT FINAL NUMERICAL ANSWER:
            From the text below, extract ONLY the final numerical answer.
            - Remove all text, units, commas, and explanations.
            - If answer is in \\boxed{{}}, extract content inside.
            - If decimal, preserve decimal point (e.g., "3.14" not "3,14").
            - Output NOTHING except the number (integer or decimal).
            
            Example outputs: "42", "3.14", "0", "1000"
            
            If multiple numbers, select the one that answers the original question.
            If no clear answer, output "0" as fallback.""",
            context=current_solution
        )

        # Clean output (remove any lingering text)
        # Use regex to extract only digits and decimal point
        match = re.search(r'[\d.]+', final_answer)
        if match:
            return match.group(0)
        else:
            return "0"  # Fallback