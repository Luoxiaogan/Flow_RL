# Workflow ID: mgsmbn_81_0
# Benchmark: mgsmbn
# Data Indices: [187]

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
        Universal Workflow for MGSM Bengali Math Problems
        Architecture: Reflective Diamond with Adaptive Validation
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL PROBLEM FRAMING
        # Generate 3 different interpretations of the problem's mathematical structure
        framing_instructions = [
            """Analyze the Bengali word problem and extract its mathematical skeleton.
            Step 1: List all named entities (people, objects, animals) and their associated quantities.
            Step 2: Identify all verbs/actions that imply mathematical operations (add, subtract, multiply, divide, compare).
            Step 3: Map relationships between quantities (ratios, proportions, totals, differences).
            Step 4: Define what is being asked for (the unknown).
            Step 5: Propose the sequence of operations needed to solve it.
            Format output as numbered steps with clear labels.""",
            
            """Interpret the problem as an algebraic word problem.
            Step 1: Assign variables to unknown quantities.
            Step 2: Translate each sentence into an equation or inequality.
            Step 3: Identify dependencies between equations.
            Step 4: Determine the solving strategy (substitution, elimination, direct calculation).
            Step 5: Note any implicit constraints (non-negative, integer-only, etc.).
            Present as structured mathematical modeling steps.""",
            
            """Approach the problem from a unit-tracking and real-world plausibility perspective.
            Step 1: Identify all units mentioned (টাকা, ঘণ্টা, জিনিস, etc.) and ensure consistency.
            Step 2: Flag any operations that might violate real-world constraints (fractional people, negative time).
            Step 3: Estimate expected magnitude of answer (order of magnitude check).
            Step 4: Identify potential pitfalls or ambiguous phrasings in the Bengali text.
            Step 5: Suggest validation criteria for the final answer.
            Format as a practical reasoning checklist."""
        ]

        framing_results = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in framing_instructions]
        )

        # PHASE 2: CONSTRAINT EXTRACTION & VALIDATION CRITERIA
        constraints_context = "\n\n".join([f"Perspective {i+1}:\n{res}" for i, res in enumerate(framing_results)])
        
        constraints = await self.generate(
            instruction=f"""Synthesize all perspectives below into a unified constraint framework:
            {constraints_context}
            
            Extract and list:
            1. All explicit numerical values and their meanings
            2. All implicit constraints (e.g., 'number of people' must be integer >= 0)
            3. Unit consistency requirements
            4. Expected answer type (integer, decimal, currency, etc.)
            5. Validation rules the final answer must satisfy
            
            Format as a structured JSON-like outline with clear section headers.""",
            context=constraints_context
        )

        # PHASE 3: PARALLEL SOLUTION ATTEMPTS
        solution_instructions = [
            """Using the problem structure and constraints, solve step by step:
            - Show all intermediate calculations
            - Justify each operation with reference to the problem text
            - Track units throughout
            - Box the final answer at the end
            - Include a one-sentence plausibility check""",
            
            """Solve using algebraic formalism:
            - Define all variables clearly
            - Write equations based on problem statements
            - Show solving steps
            - Substitute back to verify
            - State final answer with units
            - Check against constraints from earlier phase""",
            
            """Solve using proportional/unit analysis:
            - Set up ratios or unit conversions explicitly
            - Cancel units to verify dimensional correctness
            - Calculate stepwise
            - Verify answer makes sense in real-world context
            - Cross-check with order-of-magnitude estimate"""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=constraints) for instr in solution_instructions]
        )

        # PHASE 4: ADVERSARIAL VALIDATION
        # Each solution is critiqued by a different validator
        validation_tasks = []
        for i, solution in enumerate(solution_attempts):
            validator_instruction = f"""CRITICALLY REVIEW the following solution attempt:
            {solution}
            
            Check against these criteria:
            1. Mathematical correctness of each step
            2. Consistency with extracted constraints and units
            3. Real-world plausibility (no fractional people, negative quantities where impossible)
            4. Alignment with original problem's intent
            5. Clear derivation from given information (no unsupported assumptions)
            
            If errors found, list them specifically. If valid, state "VALID: [reason]".
            Be brutally honest — this is for educational correctness."""
            
            validation_tasks.append(self.generate(instruction=validator_instruction, context=solution))
        
        validation_results = await asyncio.gather(*validation_tasks)

        # PHASE 5: SYNTHESIS & FINAL ANSWER EXTRACTION
        synthesis_context = "\n\n".join([
            f"=== SOLUTION ATTEMPT {i+1} ===\n{sol}\n=== VALIDATION {i+1} ===\n{val}"
            for i, (sol, val) in enumerate(zip(solution_attempts, validation_results))
        ])

        final_synthesis = await self.ensemble(
            instruction=f"""Synthesize the solution attempts and their validations below:
            {synthesis_context}
            
            Selection criteria:
            1. Prefer solutions marked "VALID" by validators
            2. If multiple valid, choose the one with clearest step-by-step reasoning
            3. If none fully valid, select the one with least severe errors and note limitations
            4. Extract ONLY the final numerical answer (integer or decimal)
            5. If answer is embedded in text, extract it precisely (e.g., "75" not "The answer is 75")
            6. If no reliable answer, output "ERROR" (should be rare)
            
            Output format: ONLY the numerical answer, nothing else.""",
            contexts_list=solution_attempts  # Ensemble over solutions, informed by validations
        )

        # PHASE 6: FINAL SANITY CHECK & TYPE VALIDATION
        # Ensure output is clean number
        try:
            # Clean the output
            cleaned = re.sub(r'[^\d\.]', '', final_synthesis.strip())
            if '.' in cleaned:
                final_answer = float(cleaned)
                # If it's effectively an integer, output as int
                if final_answer.is_integer():
                    final_answer = int(final_answer)
            else:
                final_answer = int(cleaned)
        except:
            # Fallback: return as-is if parsing fails (let downstream handle)
            final_answer = final_synthesis.strip()

        return str(final_answer)