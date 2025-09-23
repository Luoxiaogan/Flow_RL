# Workflow ID: mgsmbn_72_0
# Benchmark: mgsmbn
# Data Indices: [183]

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

        # === PHASE 1: MULTI-PERSPECTIVE PROBLEM DECOMPOSITION ===
        decomposition_tasks = [
            self.generate(
                instruction="""You are a Mathematical Entity Extractor. Your task is to parse the Bengali word problem and extract:
                1. All numerical values with their associated entities (e.g., '30টি ফায়ার টাইপ' → quantity: 30, entity: fire-type cards)
                2. All mathematical operations implied by verbs or context (e.g., 'হারিয়ে ফেলে' → subtraction, 'ক্রয় করে' → addition)
                3. Temporal or logical dependencies between operations (e.g., 'after losing 8, then buying 14')
                4. The final unknown being asked for (e.g., 'probability as percentage')
                Format your output as a structured list with clear labels for each component.""",
                context=""
            ),
            self.generate(
                instruction="""You are a Narrative Event Sequencer. Reconstruct the problem as a chronological or logical sequence of events:
                1. List events in the order they occur or must be calculated
                2. For each event, specify: actor, action, quantity, and target
                3. Identify any conditional or branching logic (e.g., 'if...then')
                4. Highlight any implicit steps not explicitly stated but required for solution
                Present as numbered steps with actor-action-object-quantity tuples.""",
                context=""
            ),
            self.generate(
                instruction="""You are a Constraint and Unit Mapper. Identify:
                1. All units of measurement (টাকা, ঘণ্টা, কার্ড, etc.) and ensure consistency
                2. Real-world constraints (e.g., no negative quantities, probabilities between 0-100%, integer people)
                3. Rounding or precision requirements (e.g., 'nearest whole number')
                4. Hidden assumptions (e.g., cards are discrete, probability is uniform)
                Format as bullet points with explicit constraint statements and unit mappings.""",
                context=""
            )
        ]
        
        decomposition_results = await asyncio.gather(*decomposition_tasks)
        
        # Synthesize into unified problem model
        problem_model = await self.ensemble(
            instruction="""You are a Problem Synthesizer. Combine the three perspectives into a single, coherent problem model:
            1. Integrate mathematical entities with event sequence and constraints
            2. Resolve any contradictions between perspectives
            3. Fill gaps using logical inference
            4. Output a structured representation with sections: [Entities], [Operations Sequence], [Constraints], [Target Unknown]
            5. Ensure all numbers, units, and dependencies are explicitly stated
            This model will be the single source of truth for solution generation.""",
            contexts_list=decomposition_results
        )

        # === PHASE 2: PARALLEL SOLUTION GENERATION ===
        solution_strategies = [
            """You are a Step-by-Step Arithmetic Solver. Solve the problem by:
            1. Following the exact sequence of operations from the problem model
            2. Showing every intermediate calculation with units
            3. Justifying each step with reference to the problem model
            4. Carrying full precision until final rounding
            5. Box the final answer at the end""",
            
            """You are an Algebraic Modeler. Solve by:
            1. Defining variables for unknowns
            2. Setting up equations based on relationships in the problem model
            3. Solving algebraically with clear equation transformations
            4. Substituting known values and showing arithmetic
            5. Box the final answer at the end""",
            
            """You are a Dimensional Analyst. Solve by:
            1. Tracking units through every operation
            2. Using unit cancellation to verify operation validity
            3. Converting units when necessary (e.g., percentage = per hundred)
            4. Ensuring final answer has correct unit/dimension
            5. Box the final answer at the end"""
        ]
        
        solution_tasks = [
            self.generate(
                instruction=f"{strategy}\n\nUse this problem model:\n{problem_model}",
                context=problem_model
            ) for strategy in solution_strategies
        ]
        
        initial_solutions = await asyncio.gather(*solution_tasks)

        # === PHASE 3: ADVERSARIAL REVISION LOOP ===
        revised_solutions = []
        for solution in initial_solutions:
            current = solution
            for revision_round in range(2):  # Up to 2 revision rounds
                revised = await self.revise(
                    instruction=f"""You are a Solution Auditor. Critically examine this solution:
                    1. Verify every arithmetic operation for accuracy
                    2. Check unit consistency throughout
                    3. Ensure all constraints from problem model are satisfied
                    4. Confirm logical flow matches event sequence
                    5. Validate final answer format (single number, proper rounding)
                    6. If any error found, correct it and explain the fix
                    7. If no errors, return solution unchanged with 'VERIFIED' tag""",
                    context=current
                )
                # If no changes needed, break early
                if "VERIFIED" in revised or current == revised:
                    break
                current = revised
            revised_solutions.append(current)

        # === PHASE 4: SOLUTION ENSEMBLE AND ADJUDICATION ===
        final_solution = await self.ensemble(
            instruction="""You are the Chief Solution Adjudicator. Evaluate all candidate solutions:
            1. Score each on: (a) Internal consistency, (b) Alignment with problem model, (c) Constraint adherence, (d) Arithmetic accuracy
            2. If one solution is clearly superior, select it
            3. If multiple are equally valid, synthesize a hybrid using the most reliable steps from each
            4. Ensure final solution has clear step-by-step reasoning and boxed final answer
            5. Add '[FINAL VERDICT]' tag at start of output""",
            contexts_list=revised_solutions
        )

        # === PHASE 5: ANSWER EXTRACTION AND NORMALIZATION ===
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from this solution:
            1. Locate the boxed answer or final numerical result
            2. Remove all units, percentages, or explanatory text
            3. Apply any rounding specified in problem (e.g., nearest whole number)
            4. Return ONLY the number as a string (e.g., "33", "14.5")
            5. If multiple numbers appear, use the one that matches the problem's requested format
            6. Validate against problem constraints (e.g., probability must be 0-100)
            
            Solution to extract from:
            {final_solution}""",
            context=final_solution
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer.strip())
        return cleaned