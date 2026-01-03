# Workflow ID: mgsmbn_78_0
# Benchmark: mgsmbn
# Data Indices: [186, 46]

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

        # STEP 1: CLASSIFY PROBLEM STRUCTURE
        classification = await self.generate(
            instruction="""Analyze this Bengali math problem and produce a structured classification with these sections:
            1. PROBLEM TYPE: Identify primary category (comparison, rate, distribution, sequential, proportional, multi-entity).
            2. ENTITIES: List all named entities (people, objects) and their initial quantities/relationships.
            3. OPERATIONS: List required mathematical operations in probable execution order.
            4. TEMPORAL: Note time markers (days, steps, phases) and their sequence.
            5. CONSTRAINTS: Identify implicit constraints (non-negative, integer-only, unit consistency).
            6. TARGET: Specify what is being asked for (final quantity, difference, total, etc.).
            Format each section clearly with headers. Be exhaustive.""",
            context=""
        )

        # STEP 2: PARALLEL ENTITY & RELATIONSHIP EXTRACTION (CONSENSUS BUILDING)
        extraction_branches = await asyncio.gather(
            self.generate(
                instruction="""Extract entities and relationships focusing on NOUNS:
                - List every named person/object
                - For each, note associated numbers and comparative phrases
                - Map relationships using arrows (e.g., "Kylie → +5 shells vs Robert")
                - Ignore verbs and adverbs initially""",
                context=""
            ),
            self.generate(
                instruction="""Extract entities and relationships focusing on VERBS and ACTIONS:
                - Identify action verbs (collected, paid, divided, etc.)
                - Note subject-object relationships for each action
                - Map temporal sequence of actions
                - Quantify changes per action""",
                context=""
            ),
            self.generate(
                instruction="""Extract entities and relationships focusing on QUANTIFIERS and NUMBERS:
                - Isolate all numerical values and their descriptors
                - Note comparative operators (more than, less than, times, percent)
                - Identify base values and modifiers
                - Map mathematical dependencies""",
                context=""
            )
        )

        # Synthesize entity map from parallel extractions
        entity_map = await self.ensemble(
            instruction="""Synthesize a unified entity-relationship map from three perspectives:
            - Combine noun-based, verb-based, and quantifier-based extractions
            - Resolve conflicts by choosing most mathematically precise version
            - Format as: Entity: [name] | Initial: [value] | Relationships: [list]
            - Include temporal markers and operation dependencies
            - Flag any ambiguities for later validation""",
            contexts_list=extraction_branches
        )

        # STEP 3: PARALLEL SOLUTION ATTEMPTS (DIAMOND PATTERN)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""SOLVE USING STEP-BY-STEP ARITHMETIC:
                Problem Classification: {classification}
                Entity Map: {entity_map}
                
                Approach:
                1. Start from initial values
                2. Apply operations in chronological/sequential order
                3. Show intermediate results after each step
                4. Maintain unit tracking throughout
                5. Box final answer at end
                
                Do NOT use algebra. Use only direct calculation. Be verbose about each step.""",
                context=""
            ),
            self.generate(
                instruction=f"""SOLVE USING ALGEBRAIC MODELING:
                Problem Classification: {classification}
                Entity Map: {entity_map}
                
                Approach:
                1. Define variables for unknowns
                2. Write equations based on relationships
                3. Solve system step by step
                4. Substitute known values
                5. Box final answer
                
                Show all equation transformations. Justify each algebraic step.""",
                context=""
            ),
            self.generate(
                instruction=f"""SOLVE USING NARRATIVE SIMULATION:
                Problem Classification: {classification}
                Entity Map: {entity_map}
                
                Approach:
                1. Reconstruct problem as chronological story
                2. Simulate each event in sequence
                3. Track state changes after each event
                4. Use concrete examples if abstract
                5. Box final answer
                
                Write as if explaining to a 10-year-old. Use conversational Bengali-English mix if helpful.""",
                context=""
            )
        )

        # STEP 4: ENSEMBLE BEST SOLUTION
        draft_solution = await self.ensemble(
            instruction="""Select and synthesize the most reliable solution:
            - Compare arithmetic, algebraic, and narrative approaches
            - Prefer solutions with explicit intermediate steps
            - Check for unit consistency and constraint adherence
            - If answers differ, identify which approach handled edge cases best
            - Merge complementary explanations if needed
            - Output should be a single coherent solution with clear final answer""",
            contexts_list=solution_attempts
        )

        # STEP 5: VALIDATION & REFINEMENT LOOP (MAX 2 ITERATIONS)
        current_solution = draft_solution
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""CRITICALLY VALIDATE THIS SOLUTION:
                Original Classification: {classification}
                Entity Map: {entity_map}
                
                Check for:
                1. Arithmetic errors (recalculate key steps)
                2. Unit inconsistencies (convert if needed)
                3. Constraint violations (negative shells? fractional people?)
                4. Logical gaps (missing steps? unjustified assumptions?)
                5. Answer plausibility (does magnitude make sense?)
                
                If errors found, describe exactly what and where. If clean, say "VALIDATED".
                Be brutally honest - assume this is wrong until proven right.""",
                context=current_solution
            )

            if "VALIDATED" in validation.upper() and "ERROR" not in validation.upper():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""REVISE BASED ON VALIDATION FEEDBACK:
                    Validation Report: {validation}
                    
                    Requirements:
                    - Fix all identified errors
                    - Add missing steps or justifications
                    - Normalize units if inconsistent
                    - Round appropriately if fractional answer conflicts with context
                    - Re-box final answer
                    - Keep explanation clear and pedagogical""",
                    context=current_solution
                )

        # STEP 6: FINAL EXTRACTION & FORMATTING
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution below.
            Rules:
            - Must be a single number (integer or decimal)
            - Remove all units, explanations, and boxing
            - If multiple numbers, choose the one answering the original question
            - If no clear number, return "0" as fallback
            - Do NOT add any text - just the number""",
            context=current_solution
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        # Handle edge case where multiple numbers might remain
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        return numbers[0] if numbers else "0"