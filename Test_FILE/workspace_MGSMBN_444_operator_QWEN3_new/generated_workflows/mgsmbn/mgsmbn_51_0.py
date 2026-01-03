# Workflow ID: mgsmbn_51_0
# Benchmark: mgsmbn
# Data Indices: [24]

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

        # === STEP 1: PARALLEL SEMANTIC EXTRACTION (DIAMOND FORK 1) ===
        entity_extraction = self.generate(
            instruction="""You are a Bengali math problem semantic analyzer. Extract and structure the following with extreme precision:

1. ENTITIES: List every named person, animal, or object. For each, note role and count (e.g., "জন: caretaker, count: 1", "কুকুর: subject, count: 10").
2. QUANTITIES: List every number with its explicit unit and what it modifies (e.g., "0.5 ঘণ্টা/কুকুর/দিন", "7 দিন/সপ্তাহ").
3. RELATIONSHIPS: Describe how quantities interact (e.g., "প্রতিটি কুকুরের জন্য আলাদা সময়", "সপ্তাহ = 7 দিন").
4. GOAL: State exactly what is being asked (e.g., "মোট সপ্তাহে ব্যয়িত ঘণ্টা").

Format each section with headers: "ENTITIES:", "QUANTITIES:", "RELATIONSHIPS:", "GOAL:". Be exhaustive. Do not solve — only extract.""",
            context=""
        )

        temporal_extraction = self.generate(
            instruction="""You are a temporal and causal sequence analyzer for Bengali math problems. Your task:

1. Identify chronological order of events (e.g., "প্রথমে দৈনিক হিসাব, তারপর সাপ্তাহিক গুণ").
2. Flag dependencies (e.g., "সপ্তাহের মোট = দিনের হিসাব × 7").
3. Note implicit timeframes (e.g., "দিনে" implies daily rate, "সপ্তাহে" implies weekly total).
4. Highlight rate conversions needed (e.g., "ঘণ্টা/দিন → ঘণ্টা/সপ্তাহ").

Structure output with headers: "SEQUENCE:", "DEPENDENCIES:", "IMPLICIT TIMEFRAMES:", "RATE CONVERSIONS:". Focus only on time and causality.""",
            context=""
        )

        math_intent_extraction = self.generate(
            instruction="""You are a mathematical intent classifier and goal specifier for Bengali word problems. Analyze:

1. PROBLEM TYPE: Classify as Rate, Proportional, Distribution, Comparison, Multi-entity, or Sequential.
2. OPERATIONS NEEDED: List required math operations in order (e.g., "Multiply daily rate by days, then by dogs").
3. UNKNOWN VARIABLE: State what must be solved for (e.g., "Total hours per week").
4. CONSTRAINTS: Note real-world limits (e.g., "No negative time", "Whole dogs only").

Format: "TYPE:", "OPERATIONS:", "UNKNOWN:", "CONSTRAINTS:". Do not compute — only classify and specify.""",
            context=""
        )

        # Execute parallel extraction
        extractions = await asyncio.gather(entity_extraction, temporal_extraction, math_intent_extraction)
        entity_ext, temporal_ext, math_ext = extractions

        # === STEP 2: ENSEMBLE SYNTHESIS WITH CONFLICT DETECTION ===
        synthesis = await self.ensemble(
            instruction="""You are a synthesis and conflict detection engine. Merge these three analyses into one coherent problem model. Then:

1. COMBINE: Integrate entities, quantities, sequences, and math intent into a unified description.
2. DETECT: Flag any inconsistencies (e.g., "Temporal mentions weekly conversion but Quantity extraction missed it", "Math intent says 'multiply' but Sequence implies addition").
3. RESOLVE: If conflict is resolvable with context, resolve it. If not, explicitly state "CONFLICT: [description]".
4. OUTPUT: Present merged model first, then "CONFLICT ANALYSIS:" section.

Your output must end with either "NO_CONFLICT" or "CONFLICT_DETECTED" for downstream branching.""",
            contexts_list=extractions
        )

        # === STEP 3: CONDITIONAL REVISION LOOP (ADAPTIVE DEPTH) ===
        current_synthesis = synthesis
        for attempt in range(2):  # Max 2 revision attempts
            if "CONFLICT_DETECTED" in current_synthesis:
                # Revise each extraction using conflict feedback
                revised_extractions = await asyncio.gather(
                    self.revise(
                        instruction=f"""Conflict detected in synthesis: {current_synthesis}
Revise your entity/quantity extraction to resolve stated conflicts. Preserve structure. Add missing conversions or dependencies.""",
                        context=entity_ext
                    ),
                    self.revise(
                        instruction=f"""Conflict detected in synthesis: {current_synthesis}
Revise your temporal/sequence extraction to resolve stated conflicts. Clarify dependencies and rate conversions.""",
                        context=temporal_ext
                    ),
                    self.revise(
                        instruction=f"""Conflict detected in synthesis: {current_synthesis}
Revise your math intent extraction to align with temporal and entity corrections. Update operations and constraints if needed.""",
                        context=math_ext
                    )
                )
                entity_ext, temporal_ext, math_ext = revised_extractions
                
                # Re-synthesize
                current_synthesis = await self.ensemble(
                    instruction="""Re-synthesize after conflict resolution. Same format as before. Be stricter in conflict detection.""",
                    contexts_list=revised_extractions
                )
            else:
                break

        # === STEP 4: PARALLEL SOLUTION GENERATION (DIAMOND FORK 2) ===
        arithmetic_solution = self.generate(
            instruction=f"""Using this problem model: {current_synthesis}

Solve using DIRECT ARITHMETIC SEQUENCING:
1. Write each calculation step explicitly (e.g., "Step 1: 10 dogs × 0.5 hours/dog/day = 5 hours/day").
2. Show unit propagation at each step.
3. Chain operations chronologically.
4. Box final answer as: FINAL_ANSWER: <number>

Do not use algebra — only arithmetic chaining.""",
            context=current_synthesis
        )

        algebraic_solution = self.generate(
            instruction=f"""Using this problem model: {current_synthesis}

Solve using ALGEBRAIC MODELING:
1. Define variables for unknowns (e.g., "Let T = total weekly hours").
2. Write equations based on relationships (e.g., "T = dogs × hours_per_dog_per_day × days_per_week").
3. Substitute known values.
4. Solve equation step-by-step.
5. Box final answer as: FINAL_ANSWER: <number>

Show all algebraic manipulations.""",
            context=current_synthesis
        )

        dimensional_solution = self.generate(
            instruction=f"""Using this problem model: {current_synthesis}

Solve using DIMENSIONAL ANALYSIS:
1. Treat units as algebraic entities (e.g., "hours/dog/day × dogs × days = hours").
2. Cancel units explicitly at each multiplication/division.
3. Verify final unit matches goal unit.
4. If unit mismatch, flag error and recalculate.
5. Box final answer as: FINAL_ANSWER: <number>

Focus obsessively on unit consistency.""",
            context=current_synthesis
        )

        solutions = await asyncio.gather(arithmetic_solution, algebraic_solution, dimensional_solution)

        # === STEP 5: CROSS-VALIDATION ENSEMBLE ===
        final_answer_selection = await self.ensemble(
            instruction="""You are a solution validator and consensus builder. Given three solution attempts:

1. COMPARE: Extract the FINAL_ANSWER from each. Are they numerically identical?
2. IF TWO OR MORE AGREE: Select that answer. Confidence = High.
3. IF ALL DIFFER: Select the answer from the solution with the most rigorous unit tracking and intermediate verification. Confidence = Medium.
4. OUTPUT: ONLY the numerical answer (no text, no units). If uncertain, still pick best option.

Example output: "35" — nothing else.""",
            contexts_list=solutions
        )

        # === STEP 6: FINAL SANITY CHECK & REVISION ===
        validated_answer = await self.revise(
            instruction=f"""You are a final validator. Given the selected answer: {final_answer_selection}

1. SANITY CHECK: Is this answer contextually plausible? (e.g., "Can a week have 3500 hours?" → No. "Can 10 dogs require 35 hours/week?" → Yes).
2. UNIT CHECK: Does the number make sense with the problem's units? (e.g., fractional people? negative time?).
3. PRECISION: Is decimal precision appropriate? (e.g., .5 hours is fine; .333... may need rounding).
4. If any issue: Recalculate with corrected assumptions and output new FINAL_ANSWER: <number>.
5. If no issue: Output the same number.

Return ONLY the final numerical answer. No explanations.""",
            context=final_answer_selection
        )

        # Extract numerical answer (simple string cleanup — no imports needed)
        answer_clean = validated_answer.strip().split()[0].replace(',', '').replace('।', '')
        # Handle potential "FINAL_ANSWER: 35" format
        if ':' in answer_clean:
            answer_clean = answer_clean.split(':')[-1].strip()
        
        return answer_clean