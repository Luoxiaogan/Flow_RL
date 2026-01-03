# Workflow ID: mgsmbn_88_0
# Benchmark: mgsmbn
# Data Indices: [165]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for MGSM Bengali math word problems.
        Uses parallel extraction, adaptive strategy selection, 
        iterative validation, and ensemble synthesis.
        """
        import asyncio
        import re

        # === PHASE 1: PARALLEL EXTRACTION & DISAMBIGUATION ===
        # Extract problem components from multiple semantic angles
        extraction_tasks = [
            self.generate(
                instruction="""Extract all numerical values, named entities, and explicit relationships.
                Format as:
                NUMBERS: [value] → [what it represents]
                ENTITIES: [person/object] → [role/property]
                RELATIONSHIPS: [how entities/numbers interact]
                CONSTRAINTS: [explicit rules or conditions]
                GOAL: [what needs to be calculated]""",
                context=""
            ),
            self.generate(
                instruction="""Identify implicit assumptions, temporal sequences, and conditional logic.
                Focus on:
                - Words like 'যদি', 'তবে', 'পরে', 'আগে', 'ছাড়া'
                - Hidden operations (e.g., 'remove lowest', 'after discount')
                - Unit consistency (টাকা, ঘণ্টা, জিনিস)
                - Plausibility bounds (can't have negative people, scores >100, etc.)""",
                context=""
            ),
            self.generate(
                instruction="""Rephrase the problem in simple, unambiguous Bengali.
                Break into atomic statements.
                Resolve pronoun references (তাকে, তারা, এটি).
                Clarify ambiguous phrases (e.g., 'গড়ে 93 পেতে হলে' → 'average of remaining scores must be 93').""",
                context=""
            )
        ]
        
        extractions = await asyncio.gather(*extraction_tasks)
        
        # Synthesize into unified problem representation
        problem_repr = await self.ensemble(
            instruction="""Merge these three perspectives into one comprehensive problem representation.
            Prioritize:
            1. Completeness (all numbers, entities, constraints)
            2. Clarity (unambiguous phrasing)
            3. Structure (group related elements)
            Output format:
            ---
            NUMBERS: {list}
            ENTITIES: {list}
            CONSTRAINTS: {list}
            GOAL: {description}
            AMBIGUITIES_RESOLVED: {list}
            ---""",
            contexts_list=extractions
        )

        # === PHASE 2: PROBLEM CLASSIFICATION & STRATEGY SELECTION ===
        problem_type = await self.generate(
            instruction=f"""Classify this problem based on its mathematical structure:
            Problem Representation:
            {problem_repr}
            
            Choose ONE primary type:
            - SEQUENTIAL (multiple steps in order)
            - PROPORTIONAL (ratios, percentages, scaling)
            - RATE (speed/time, work rate, unit price)
            - DISTRIBUTION (division, sharing, remainders)
            - COMPARISON (differences, 'how many more')
            - MULTI_ENTITY (multiple actors with interdependent quantities)
            
            Then, select the MOST appropriate solution strategy:
            - Algebraic equation setup
            - Step-by-step arithmetic simulation
            - Proportional scaling
            - Unit conversion chain
            - Elimination/substitution
            - Trial and error with constraints
            
            Justify your choice in 2-3 sentences.""",
            context=problem_repr
        )

        # === PHASE 3: PARALLEL SOLUTION ATTEMPTS ===
        # Generate 3 solution attempts using different strategies
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using ALGEBRAIC approach:
                Problem: {problem_repr}
                Type: {problem_type}
                
                Steps:
                1. Define variables for unknowns
                2. Write equations based on relationships
                3. Solve step by step
                4. Box final answer as ### {{"answer": "X"}} ###
                Show ALL work. Track units. Check for constraint violations.""",
                context=problem_repr
            ),
            self.generate(
                instruction=f"""Solve using STEP-BY-STEP SIMULATION:
                Problem: {problem_repr}
                Type: {problem_type}
                
                Simulate the scenario chronologically.
                For each step:
                - State current state (who has what)
                - Apply operation
                - Update state
                - Check constraints
                End with final answer boxed as ### {{"answer": "X"}} ###""",
                context=problem_repr
            ),
            self.generate(
                instruction=f"""Solve using PROPORTIONAL/LOGICAL REASONING:
                Problem: {problem_repr}
                Type: {problem_type}
                
                Use ratios, scaling, or logical deduction.
                Avoid algebra if possible.
                Show reasoning chain.
                Verify answer makes real-world sense.
                Box final answer as ### {{"answer": "X"}} ###""",
                context=problem_repr
            )
        )

        # === PHASE 4: ENSEMBLE SELECTION & SYNTHESIS ===
        best_solution = await self.ensemble(
            instruction="""Evaluate these three solution attempts.
            Criteria:
            1. Mathematical correctness (arithmetic, logic)
            2. Adherence to problem constraints
            3. Unit consistency
            4. Real-world plausibility
            5. Clarity of steps
            
            Select the BEST solution. If multiple are valid, synthesize a hybrid.
            Output ONLY the final answer in format: ### {{"answer": "X"}} ###""",
            contexts_list=solution_attempts
        )

        # === PHASE 5: VALIDATION & REVISION LOOP (up to 3 iterations) ===
        final_answer = best_solution
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""VALIDATE this solution:
                Solution: {final_answer}
                Problem Representation: {problem_repr}
                
                Check:
                - Is the math correct? Recompute key steps.
                - Are ALL constraints satisfied? (e.g., 'remove lowest score')
                - Is the answer plausible? (e.g., score ≤100, positive people)
                - Are units consistent?
                
                If VALID: Output "VALID: ### {{"answer": "X"}} ###"
                If INVALID: Explain error and suggest fix.""",
                context=final_answer
            )
            
            if "VALID:" in validation:
                final_answer = validation
                break
            else:
                # Revise based on validation feedback
                final_answer = await self.revise(
                    instruction=f"""FIX the solution based on this validation feedback:
                    Feedback: {validation}
                    Original Solution: {final_answer}
                    Problem: {problem_repr}
                    
                    Correct errors. Maintain step-by-step reasoning.
                    Output revised answer as ### {{"answer": "X"}} ###""",
                    context=final_answer
                )
        else:
            # If all revisions fail, fall back to ensemble output
            pass

        # === PHASE 6: FINAL EXTRACTION & OUTPUT ===
        # Extract numerical answer from validated solution
        answer_extraction = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this text:
            {final_answer}
            
            Rules:
            - Must be a number (integer or decimal)
            - Remove units, labels, explanations
            - If multiple numbers, choose the one that answers the goal
            - Output format: JUST the number, nothing else""",
            context=final_answer
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        clean_answer = re.sub(r'[^\d.]', '', answer_extraction.strip())
        
        return clean_answer