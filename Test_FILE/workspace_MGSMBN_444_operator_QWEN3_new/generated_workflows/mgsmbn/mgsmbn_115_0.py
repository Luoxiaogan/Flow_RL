# Workflow ID: mgsmbn_115_0
# Benchmark: mgsmbn
# Data Indices: [72, 32]

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

        # === PHASE 1: PARALLEL PROBLEM DECONSTRUCTION (DIAMOND FORK) ===
        # Generate three complementary interpretations in parallel
        math_struct, narrative_flow, unit_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze this Bengali math problem from a purely mathematical perspective. Extract:
                - All numerical values and what they represent
                - Mathematical operations implied (add, multiply, percent, ratio, etc.)
                - Variables and unknowns to solve for
                - Any algebraic relationships or equations
                Format as a structured bullet list. Be precise and literal.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this Bengali math problem as a narrative/story. Extract:
                - Sequence of events or actions
                - Actors (people, objects) and their roles
                - Temporal or causal relationships (before/after, because/therefore)
                - What changes over time or due to actions
                Format as a chronological bullet list. Preserve story logic.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this Bengali math problem for units, constraints, and hidden conditions. Extract:
                - All units mentioned (টাকা, সেকেন্ড, গ্রাম, etc.) and ensure consistency
                - Physical or logical constraints (e.g., can't have negative time, fractional people)
                - Implicit assumptions (e.g., constant speed, equal distribution)
                - Boundary conditions or edge cases
                Format as a constraint list with unit annotations.""",
                context=""
            )
        )

        # === PHASE 2: PROBLEM CLASSIFICATION & STRATEGY SELECTION ===
        classification = await self.generate(
            instruction=f"""Based on the following analyses, classify this problem into exactly one type:
            - Sequential (steps happen in order: deposit then withdraw)
            - Proportional (ratios, percentages, scaling: calories per serving)
            - Comparative (differences, "how many more": Gerald vs Lee time)
            - Distribution (sharing, dividing, remainders: apples among children)
            - Multi-entity (multiple actors with different quantities: A has X, B has Y)
            
            Then, generate a step-by-step solving strategy tailored to this type.
            Use the extracted math structure, narrative, and constraints to inform your strategy.
            Format: "TYPE: [type] STRATEGY: [numbered steps]".""",
            context=f"Math Structure: {math_struct}\nNarrative: {narrative_flow}\nUnits/Constraints: {unit_analysis}"
        )

        # Extract type for conditional branching
        problem_type = "Comparative"  # default fallback
        if "TYPE:" in classification:
            problem_type = classification.split("TYPE:")[1].split()[0].strip()

        # === PHASE 3: ITERATIVE CALCULATION WITH VALIDATION (CASCADE) ===
        current_context = f"Strategy: {classification}\nMath: {math_struct}\nNarrative: {narrative_flow}\nConstraints: {unit_analysis}"
        solution_attempt = ""
        
        for step_num in range(4):  # max 4 steps
            # Generate calculation step
            step_calc = await self.generate(
                instruction=f"""Execute STEP {step_num + 1} of the solving strategy below. 
                Show explicit arithmetic. Track units. Output intermediate result.
                If final answer reached, output ONLY the number (integer or decimal).
                Strategy: {classification}
                Previous steps: {solution_attempt}""",
                context=current_context
            )
            
            # Validate the step
            validation = await self.generate(
                instruction=f"""Critically validate this calculation step:
                - Check arithmetic for errors
                - Verify unit consistency (e.g., seconds vs minutes)
                - Ensure no violation of constraints (no negative people, etc.)
                - Flag if answer is incomplete or illogical
                If valid, output 'VALID: [summary]'. If invalid, output 'INVALID: [detailed reason] and suggest fix'.""",
                context=step_calc
            )
            
            if "INVALID" in validation:
                # Revise the step with error correction
                step_calc = await self.revise(
                    instruction=f"""Fix the errors identified in validation:
                    Validation Feedback: {validation}
                    Original Step: {step_calc}
                    Correct the calculation, units, or logic. Be precise.""",
                    context=step_calc
                )
            
            # Append to solution attempt
            solution_attempt += f"\nSTEP {step_num + 1}: {step_calc}"
            
            # Early termination if final number detected
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', step_calc)
            if numbers and "STEP" not in step_calc and len(numbers) == 1:
                final_answer = numbers[0]
                break
        else:
            # If no early break, extract last number as fallback
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', solution_attempt)
            final_answer = numbers[-1] if numbers else "0"

        # === PHASE 4: ENSEMBLE SYNTHESIS WITH FALLBACK (DIAMOND MERGE) ===
        # Generate a fallback "direct solve" attempt in parallel
        direct_solve = await self.generate(
            instruction="""Ignore all previous analysis. Directly solve the original Bengali problem:
            - Translate key phrases to mathematical expressions
            - Compute answer in one step if possible
            - Output ONLY the final number
            This is a fallback for simple problems.""",
            context=""
        )

        # Ensemble between main solution and fallback
        final_result = await self.ensemble(
            instruction=f"""Select the best final answer from these candidates:
            Candidate 1 (Main Workflow): {final_answer}
            Candidate 2 (Direct Solve): {direct_solve}
            
            Selection Criteria:
            1. Numerical correctness (verify against problem logic)
            2. Unit consistency (must match problem's expected unit)
            3. Contextual plausibility (no negative time, fractional people unless allowed)
            4. Prefer explicit step-by-step derivation over guess
            Output ONLY the selected number.""",
            contexts_list=[final_answer, direct_solve]
        )

        # Extract clean number from ensemble result
        clean_numbers = re.findall(r'[-+]?\d*\.\d+|\d+', final_result)
        return clean_numbers[0] if clean_numbers else "0"