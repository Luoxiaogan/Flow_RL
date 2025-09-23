# Workflow ID: mgsmbn_68_0
# Benchmark: mgsmbn
# Data Indices: [136, 184]

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
        Universal Workflow for MGSM Bengali Math Word Problems
        Architecture: Adaptive Diamond-Feedback Hybrid
        """
        import asyncio
        import re

        # === PHASE 1: PARALLEL STRUCTURAL DECOMPOSITION ===
        # Extract problem components through multiple independent lenses
        decomposition_tasks = [
            self.generate(
                instruction="""Perform mathematical decomposition:
                1. Identify all numerical values and their associated entities (e.g., 'জিমির কাছে $18' → entity: জিমি, value: 18, unit: টাকা)
                2. Extract all mathematical relationships (e.g., 'দ্বিগুণ', 'বেশি', 'কম', 'ভাগ')
                3. Determine the target unknown (what is being asked)
                4. List implicit constraints (e.g., non-negative, integer-only)
                Format as structured JSON with keys: numbers, relationships, target, constraints""",
                context=""
            ),
            self.generate(
                instruction="""Perform narrative decomposition:
                1. Identify all actors (people, objects) and their roles
                2. Sequence events chronologically
                3. Extract conditional statements or hypotheticals
                4. Note any comparisons or relative quantities
                Format as structured JSON with keys: actors, events, conditionals, comparisons""",
                context=""
            ),
            self.generate(
                instruction="""Perform unit and context analysis:
                1. Identify all units (টাকা, ঘণ্টা, জিনিস, etc.) and their contexts
                2. Flag any unit conversions needed
                3. Identify real-world constraints (e.g., can't have negative money, fractional people)
                4. Note any scaling factors (percentages, ratios, multiples)
                Format as structured JSON with keys: units, conversions, constraints, scaling""",
                context=""
            )
        ]
        
        decompositions = await asyncio.gather(*decomposition_tasks)
        
        # === PHASE 2: SYNTHESIZE UNIFIED PROBLEM MODEL ===
        unified_model = await self.ensemble(
            instruction="""Synthesize a unified mathematical model from the three decompositions:
            1. Combine numerical values with their entities and relationships
            2. Integrate chronological events with mathematical operations
            3. Apply unit constraints and scaling factors
            4. Formulate step-by-step calculation plan with explicit operations
            5. Include unit tracking at each step
            Output format: 
            {
                "steps": [
                    {"operation": "multiply", "operands": [2, 8], "unit": "টাকা", "description": "জিমির অর্থ = 2 × এথেলের অর্থ"},
                    {"operation": "add", "operands": [16, 2], "unit": "টাকা", "description": "জিমির অর্থ + 2"}
                ],
                "target": "final_value",
                "constraints": ["non_negative", "integer_if_people"]
            }""",
            contexts_list=decompositions
        )

        # === PHASE 3: GENERATE MULTIPLE SOLUTION PATHS ===
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution Path A (Direct Calculation):
                Using the unified model: {unified_model}
                Execute calculations step by step.
                Show all intermediate results with units.
                Verify unit consistency at each step.
                Format: Step-by-step calculation with final answer boxed.""",
                context=unified_model
            ),
            self.generate(
                instruction=f"""Generate solution Path B (Algebraic Modeling):
                Using the unified model: {unified_model}
                Define variables for unknowns.
                Set up equations based on relationships.
                Solve algebraically.
                Substitute known values.
                Format: Equation setup → solution steps → final answer boxed.""",
                context=unified_model
            )
        )

        # === PHASE 4: ENSEMBLE SYNTHESIS & VALIDATION ===
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from Path A and Path B:
            1. Compare intermediate steps for consistency
            2. Verify unit handling in both paths
            3. Check for adherence to constraints
            4. Select the most reliable path or merge compatible elements
            5. Output only the final numerical answer with unit if applicable
            6. If paths conflict, flag for revision""",
            contexts_list=solution_paths
        )

        # === PHASE 5: REVERSE VALIDATION ===
        validation = await self.generate(
            instruction=f"""Validate the solution by reverse-engineering:
            Given answer: {synthesized_solution}
            Work backward through the problem:
            1. Does this answer satisfy all stated conditions?
            2. Does it violate any constraints (negative, fractional people)?
            3. Are units consistent throughout?
            4. If invalid, explain why and suggest correction.
            Output: "VALID" or "INVALID: [reason]" """,
            context=synthesized_solution
        )

        # === PHASE 6: CONDITIONAL REFINEMENT ===
        final_answer = synthesized_solution
        if "INVALID" in validation:
            # Revise based on validation feedback
            final_answer = await self.revise(
                instruction=f"""Revise the solution based on validation feedback:
                Validation: {validation}
                Original model: {unified_model}
                Previous answer: {synthesized_solution}
                Correct errors in logic, units, or constraints.
                Output only the corrected numerical answer.""",
                context=synthesized_solution
            )

        # === PHASE 7: OUTPUT SANITIZATION ===
        sanitized_answer = await self.summarize(
            instruction="""Extract and sanitize the final numerical answer:
            1. Remove all explanatory text, units, and formatting
            2. Ensure it's a pure number (integer or decimal)
            3. If context implies integer (people, items), round to nearest integer
            4. If currency, round to 2 decimal places
            5. Clamp to domain constraints (non-negative, etc.)
            Output: ONLY the numerical value, nothing else.""",
            context=final_answer
        )

        # Clean and return
        # Extract number from text (handles cases where summarization might leave text)
        match = re.search(r'[-+]?\d*\.\d+|\d+', sanitized_answer)
        if match:
            result = match.group(0)
            # Convert to float then to int if whole number
            num = float(result)
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        else:
            # Fallback: return as-is (shouldn't happen with proper sanitization)
            return sanitized_answer.strip()