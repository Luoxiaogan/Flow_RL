# Workflow ID: mgsmbn_60_0
# Benchmark: mgsmbn
# Data Indices: [108]

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

        # === PHASE 1: PARALLEL EXTRACTION (FORK) ===
        # Extract core components simultaneously for robustness
        entity_task = self.generate(
            instruction="""Extract all named entities and their roles from the Bengali problem.
            Focus on: people (names, pronouns), time periods (days, dates), objects (items, quantities).
            Format as bullet points with Bengali terms and English translations in parentheses.
            Example: "- সোমবার (Monday) - starting day"
            Be exhaustive - even implied entities matter.""",
            context=""
        )
        
        quantity_task = self.generate(
            instruction="""Extract all numerical values and their associated units/contexts.
            For each number, specify:
            - The exact Bengali phrase containing it
            - What it quantifies (distance, time, count, money, etc.)
            - Its unit (মাইল, টাকা, জিনিস, ঘণ্টা, etc.)
            - Whether it's a known value or unknown (to solve for)
            Format as numbered list with clear annotations.""",
            context=""
        )
        
        relation_task = self.generate(
            instruction="""Extract all mathematical relationships and operations implied in the text.
            Identify:
            - Comparative phrases (বেশি, কম, গুণ, ভাগ, অংশ)
            - Temporal sequences (পরে, আগে, থেকে)
            - Logical dependencies (যদি, তবে, যখন)
            - Hidden operations (e.g., '6 গুণ বেশি' implies multiplication AND addition)
            Map each to potential arithmetic operations (+, -, ×, ÷, =).
            Provide examples from the text with operation mappings.""",
            context=""
        )
        
        constraint_task = self.generate(
            instruction="""Identify all explicit and implicit constraints.
            Consider:
            - Physical impossibilities (negative quantities, fractional people)
            - Unit consistency requirements
            - Boundary conditions (minimum/maximum values)
            - Real-world logic (can't walk negative miles)
            - Sequential dependencies (must happen before/after)
            List each constraint with justification from the problem text.""",
            context=""
        )

        # Execute all extractions in parallel
        entity_extract, quantity_extract, relation_extract, constraint_extract = await asyncio.gather(
            entity_task, quantity_task, relation_task, constraint_task
        )

        # === PHASE 2: CROSS-VALIDATION & REFINEMENT (REVISE LOOP) ===
        # Revise each component by cross-referencing others
        refined_entities = await self.revise(
            instruction=f"""Improve entity extraction by cross-referencing with quantities and relations.
            Given:
            - Quantities: {quantity_extract[:500]}
            - Relations: {relation_extract[:500]}
            
            Tasks:
            1. Add any entities implied by quantities (e.g., if "4 miles" is mentioned, ensure "walker" is identified)
            2. Resolve ambiguities using relational context (e.g., "he" refers to which named person?)
            3. Flag any entity without associated quantities as potential error
            4. Ensure temporal entities are ordered chronologically
            Output revised entity list with confidence annotations.""",
            context=entity_extract
        )

        refined_quantities = await self.revise(
            instruction=f"""Refine quantity extraction using entity and relation context.
            Given:
            - Entities: {refined_entities[:500]}
            - Relations: {relation_extract[:500]}
            
            Tasks:
            1. Attach quantities to specific entities (e.g., "4 miles" → "Walt on Monday")
            2. Convert all units to consistent format (e.g., 'মাইল' → 'miles')
            3. Identify which quantity is the unknown to solve for
            4. Flag any quantity without clear entity association
            Output structured table: Entity | Quantity | Unit | Known/Unknown""",
            context=quantity_extract
        )

        refined_relations = await self.revise(
            instruction=f"""Enhance relationship extraction using entity and quantity context.
            Given:
            - Entities: {refined_entities[:500]}
            - Quantities: {refined_quantities[:500]}
            
            Tasks:
            1. Map relationships to specific entity-quantity pairs
            2. Resolve ambiguous operations (e.g., '6 গুণ বেশি' = 6×original or 7×original?)
            3. Sequence operations chronologically where time-based
            4. Identify which relationships involve the unknown quantity
            Output as ordered list of operations with entity/quantity references.""",
            context=relation_extract
        )

        # === PHASE 3: PARALLEL SOLUTION GENERATION (DIAMOND FORK) ===
        # Generate multiple solution approaches simultaneously
        algebraic_approach = await self.generate(
            instruction=f"""Solve using algebraic modeling.
            Steps:
            1. Assign variables to unknown quantities
            2. Translate relationships into equations
            3. Solve system of equations step by step
            4. Show all algebraic manipulations
            5. Verify solution satisfies all constraints
            Use quantities: {refined_quantities[:300]}
            Use relations: {refined_relations[:300]}
            Output final answer as: "ANSWER: <number>""",
            context=""
        )

        procedural_approach = await self.generate(
            instruction=f"""Solve using step-by-step procedural calculation.
            Steps:
            1. Start with known quantities
            2. Apply operations in chronological/logical order
            3. Show intermediate results with units
            4. Track unit consistency at each step
            5. Arrive at final answer through sequential computation
            Use entities: {refined_entities[:300]}
            Use relations: {refined_relations[:300]}
            Output final answer as: "ANSWER: <number>""",
            context=""
        )

        unit_analysis_approach = await self.generate(
            instruction=f"""Solve using dimensional analysis and unit tracking.
            Steps:
            1. Identify target unit for final answer
            2. Map all quantities to target unit dimension
            3. Apply operations only when units are compatible
            4. Cancel units systematically
            5. Final answer must have correct unit dimension
            Use quantities: {refined_quantities[:300]}
            Use constraints: {constraint_extract[:300]}
            Output final answer as: "ANSWER: <number>""",
            context=""
        )

        # === PHASE 4: ENSEMBLE SYNTHESIS WITH ERROR LOCALIZATION ===
        candidate_solutions = [algebraic_approach, procedural_approach, unit_analysis_approach]
        
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the most reliable solution from candidates.
            Evaluation criteria:
            1. Mathematical correctness (verify calculations)
            2. Unit consistency throughout
            3. Narrative consistency with problem text
            4. Handling of edge cases (negatives, fractions, etc.)
            5. Explicit step-by-step verification shown
            
            For conflicting answers:
            - Trace back to which extraction component (entities, quantities, relations) caused discrepancy
            - Prefer solutions whose extraction components had higher confidence annotations
            - If still uncertain, choose simplest consistent solution
            
            Output ONLY the final numerical answer as: "ANSWER: <number>""",
            contexts_list=candidate_solutions
        )

        # === PHASE 5: VALIDATION & FORMATTING (CASCADE FEEDBACK) ===
        # Extract just the number from synthesized solution
        answer_match = re.search(r'ANSWER:\s*([\-]?\d+\.?\d*)', synthesized_solution)
        if answer_match:
            raw_answer = answer_match.group(1)
            # Validate and format final answer
            final_answer = await self.revise(
                instruction=f"""Validate and format the numerical answer.
                Given raw answer: {raw_answer}
                Tasks:
                1. Verify it satisfies all original constraints
                2. Ensure no unit conversion errors
                3. Check for contextual plausibility (no negative apples, etc.)
                4. Format as clean number (remove trailing .0 if integer)
                5. If validation fails, explain why and suggest correction
                Output ONLY the final validated number.""",
                context=synthesized_solution
            )
            return final_answer.strip()
        else:
            # Fallback: return ensemble output as-is if parsing fails
            return synthesized_solution.strip()