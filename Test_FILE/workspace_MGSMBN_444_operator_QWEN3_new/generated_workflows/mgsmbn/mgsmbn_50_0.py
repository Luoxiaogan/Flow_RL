# Workflow ID: mgsmbn_50_0
# Benchmark: mgsmbn
# Data Indices: [194, 145]

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

        # === PHASE 1: PARALLEL PROBLEM DECONSTRUCTION ===
        # Extract raw entities & classify problem type simultaneously
        entity_extraction_task = self.generate(
            instruction="""Extract ALL numerical values, named entities, units, and explicit relationships from the problem.
            Format as:
            NUMBERS: [list with descriptions]
            ENTITIES: [people, objects, time periods]
            UNITS: [টাকা, ঘণ্টা, পৃষ্ঠা, etc.]
            RELATIONSHIPS: [what affects what, in chronological or causal order]
            CONSTRAINTS: [explicit or implicit limits, e.g., 'can't be negative']""",
            context=""
        )
        
        problem_classification_task = self.generate(
            instruction="""Classify this problem with deep analysis:
            1. Problem Type: Sequential, Proportional, Rate-Based, Distribution, Comparison, Multi-Entity?
            2. Required Operations: List all math operations needed (add, mult, div, unit conv, etc.)
            3. Hidden Steps: Are there unstated calculations? (e.g., 'replies equally' implies doubling)
            4. Output Format: Expected answer type (integer, decimal, unit-bound)
            5. Complexity Level: Simple (1-2 steps), Medium (3-4), Complex (5+ or nested)
            6. Potential Pitfalls: What could go wrong? (unit mismatch, order error, etc.)
            Provide structured, detailed classification.""",
            context=""
        )

        # Run in parallel
        entity_extraction, problem_classification = await asyncio.gather(
            entity_extraction_task, problem_classification_task
        )

        # Merge into unified schema
        problem_schema = await self.ensemble(
            instruction="""Synthesize the entity extraction and problem classification into a single Unified Problem Schema.
            Include:
            - All key numbers and what they represent
            - Problem type and required operations
            - Step-by-step dependencies (what must be calculated first)
            - Units and conversion needs
            - Validation constraints (e.g., 'answer must be positive integer')
            Format clearly for use in solution generation.""",
            contexts_list=[entity_extraction, problem_classification]
        )

        # === PHASE 2: PARALLEL SOLUTION PATH GENERATION ===
        # Generate 3 distinct solution approaches
        path_a = self.generate(
            instruction=f"""SOLUTION PATH A: Literal Narrative Translation
            Using the problem schema:
            {problem_schema}
            
            Solve by following the story chronologically. Convert each sentence into a calculation step.
            - Write explicit formulas for each step
            - Track units at every stage
            - Show intermediate results
            - Final answer must be numerical only""",
            context=problem_schema
        )

        path_b = self.generate(
            instruction=f"""SOLUTION PATH B: Algebraic Modeling
            Using the problem schema:
            {problem_schema}
            
            Assign variables to unknowns. Set up equations based on relationships.
            - Define variables clearly
            - Show equation setup and solving steps
            - Substitute known values
            - Track units dimensionally
            - Final answer must be numerical only""",
            context=problem_schema
        )

        path_c = self.generate(
            instruction=f"""SOLUTION PATH C: Unit-Driven Dimensional Analysis
            Using the problem schema:
            {problem_schema}
            
            Start from target unit (e.g., ঘণ্টা) and work backward using multiplication/division of given rates and quantities.
            - Write unit fractions explicitly
            - Cancel units step by step
            - Show dimensional consistency
            - Final answer must be numerical only""",
            context=problem_schema
        )

        # Run all solution paths in parallel
        solutions = await asyncio.gather(path_a, path_b, path_c)

        # === PHASE 3: VALIDATION & REFINEMENT LOOP ===
        refined_solutions = []
        for i, solution in enumerate(solutions):
            current = solution
            for iteration in range(2):  # Max 2 refinement loops
                validation = await self.generate(
                    instruction=f"""CRITIC VALIDATION for Solution {chr(65+i)}:
                    Check for:
                    1. Unit consistency throughout
                    2. Mathematical correctness (arithmetic, order of ops)
                    3. Contextual plausibility (no negative people, fractional items unless allowed)
                    4. Alignment with problem schema
                    5. Completeness (all steps accounted for)
                    If errors found, describe them specifically. If clean, say 'VALID'.""",
                    context=current
                )
                
                if "VALID" not in validation.upper():
                    current = await self.revise(
                        instruction=f"""REVISE based on validation feedback:
                        {validation}
                        
                        Fix all identified errors. Maintain step-by-step clarity. Preserve unit tracking.
                        Ensure final output is a single numerical value.""",
                        context=current
                    )
                else:
                    break
            refined_solutions.append(current)

        # === PHASE 4: ENSEMBLE SYNTHESIS & FINAL OUTPUT ===
        final_answer = await self.ensemble(
            instruction="""FINAL SYNTHESIS:
            You have 3 solution paths (possibly refined). Your task:
            1. Compare numerical results. If all agree, return that number.
            2. If they disagree, analyze which solution best satisfies:
               - Unit consistency
               - Step completeness
               - Alignment with problem schema
               - Contextual plausibility
            3. Output ONLY the final numerical answer as a single value (integer or decimal).
            4. NO explanations, NO units, NO markdown — just the number.
            Example: "3" or "20.5" — nothing else.""",
            contexts_list=refined_solutions
        )

        # Final cleanup: ensure pure numerical output
        cleaned_answer = await self.revise(
            instruction="""FINAL OUTPUT SANITIZATION:
            Extract ONLY the numerical value from the text below. Remove all units, labels, explanations, and formatting.
            If decimal, use minimal necessary precision (no trailing zeros unless significant).
            If integer, output as integer.
            Return ONLY the number, nothing else.""",
            context=final_answer
        )

        # Use regex to extract number if needed (fallback)
        number_match = re.search(r'[-+]?\d*\.?\d+', cleaned_answer)
        if number_match:
            return number_match.group(0)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return cleaned_answer.strip()