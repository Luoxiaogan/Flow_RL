# Workflow ID: mgsmbn_120_0
# Benchmark: mgsmbn
# Data Indices: [54]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: SEMANTIC DECOMPOSITION
        # Break the Bengali word problem into conceptual subproblems with dependencies
        decomposition_instruction = """
        You are a mathematical linguist specializing in Bengali elementary word problems.
        Your task is to decompose the problem into atomic, solvable subproblems that capture:
        - Entity identification (people, objects, units)
        - Numerical relationships (what depends on what)
        - Temporal or logical sequencing
        - Implicit constraints (real-world plausibility)

        For each subproblem:
        - Assign a unique ID (e.g., SP1, SP2)
        - Write a clear, imperative description of what must be calculated or determined
        - List dependency IDs (comma-separated) if this step relies on others

        Example format:
        [
          {"id": "SP1", "description": "Calculate total cost of phones before interest", "dependencies": ""},
          {"id": "SP2", "description": "Calculate total interest based on 2% per phone", "dependencies": "SP1"},
          {"id": "SP3", "description": "Calculate monthly payment over 3 months", "dependencies": "SP1,SP2"}
        ]

        Focus on MEANING, not computation. Do not solve — only structure.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # STEP 2: AMBIGUITY RESOLUTION (PARALLEL FORK)
        # Generate multiple interpretations of ambiguous phrases
        ambiguity_instruction = """
        Identify the most ambiguous or culturally nuanced phrase in the original Bengali problem.
        Generate THREE distinct, plausible interpretations of that phrase.
        For each, explain:
        - What the phrase could mean mathematically
        - Why this interpretation is linguistically defensible
        - What calculation would change under this interpretation

        Format each interpretation as a standalone paragraph.
        """
        interpretations = await asyncio.gather(
            self.generate(instruction=ambiguity_instruction, context=""),
            self.generate(instruction=ambiguity_instruction, context=""),
            self.generate(instruction=ambiguity_instruction, context="")
        )

        # Ensemble-select the most contextually and mathematically consistent interpretation
        ensemble_instruction = """
        You are a Bengali math textbook editor. Evaluate the three interpretations below.
        Select the ONE that is:
        - Most consistent with elementary-level problem conventions
        - Mathematically simplest unless complexity is explicitly required
        - Linguistically faithful to the original Bengali phrasing

        Return ONLY the selected interpretation. Do not add commentary.
        """
        selected_interpretation = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=interpretations
        )

        # STEP 3: CALCULATION SPECIFICATION GENERATION
        # Convert subproblems + selected interpretation into executable specification
        spec_instruction = f"""
        Using the decomposed subproblems and the selected interpretation below, generate a
        precise, step-by-step calculation specification for a Python programmer.

        Selected Interpretation:
        {selected_interpretation}

        Rules:
        - Use clear variable names (e.g., total_cost, monthly_payment)
        - Specify units at every step (টাকা, ঘণ্টা, etc.)
        - Include formulas in comments
        - Handle edge cases: no negative quantities, discrete items must be whole numbers
        - Preserve decimal precision until final step, then round appropriately for context

        Output format:
        # Step 1: [Description]
        # Formula: [math expression]
        var1 = [calculation]

        # Step 2: [Description]
        ...
        """
        calculation_spec = await self.generate(
            instruction=spec_instruction,
            context=str(subproblems)
        )

        # STEP 4: ITERATIVE EXECUTION & VALIDATION LOOP
        final_answer = None
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Execute the calculation
                code_result = await self.programmer(
                    instruction="""
                    Execute the calculation specification below. Return ONLY the final numerical answer.
                    If any step produces an illogical result (negative money, fractional people, etc.),
                    raise an exception with 'INVALID_RESULT' so the workflow can revise.
                    """,
                    context=calculation_spec,
                    max_retries=1
                )

                # Extract numerical answer (handle various output formats)
                answer_match = re.search(r'[-+]?\d*\.\d+|\d+', code_result)
                if answer_match:
                    candidate_answer = float(answer_match.group())
                    
                    # Validate reasonableness
                    validation = await self.generate(
                        instruction=f"""
                        Validate this answer: {candidate_answer}
                        Check:
                        1. Is it positive? (unless context allows negative)
                        2. Are units preserved? (e.g., no fractional phones if problem implies whole items)
                        3. Is magnitude reasonable? (e.g., monthly payment shouldn't exceed total cost)
                        4. Does it match expected precision? (round to integer if currency in context implies whole numbers)

                        If valid, return "VALID". If invalid, return "INVALID: [reason]".
                        """,
                        context=calculation_spec
                    )

                    if "VALID" in validation:
                        final_answer = candidate_answer
                        break
                    else:
                        # Revise specification based on validation feedback
                        calculation_spec = await self.revise(
                            instruction=f"""
                            Revise the calculation specification to fix this issue: {validation}
                            Preserve all correct parts. Only modify what's necessary.
                            Consider: unit conversion, formula error, misinterpretation of dependency.
                            """,
                            context=calculation_spec
                        )
                else:
                    raise ValueError("No numerical answer found in result")

            except Exception as e:
                if "INVALID_RESULT" in str(e) or retry_count == max_retries - 1:
                    # Final attempt: regenerate specification from scratch
                    calculation_spec = await self.generate(
                        instruction=f"""
                        REGENERATE the calculation specification from scratch.
                        Previous version failed. Focus on:
                        - Simpler assumptions
                        - Explicit unit handling
                        - Step-by-step verification in comments
                        """,
                        context=str(subproblems) + "\n" + selected_interpretation
                    )
                else:
                    # Minor revision on existing spec
                    calculation_spec = await self.revise(
                        instruction="Fix computational logic. Ensure all formulas are dimensionally consistent.",
                        context=calculation_spec
                    )

            retry_count += 1

        # STEP 5: FINAL ANSWER EXTRACTION & ROUNDING
        if final_answer is None:
            # Fallback: extract from last code result
            answer_match = re.search(r'[-+]?\d*\.\d+|\d+', code_result)
            final_answer = float(answer_match.group()) if answer_match else 0.0

        # Round to integer if context suggests whole numbers (currency, countable items)
        if final_answer == int(final_answer):
            final_answer = int(final_answer)
        else:
            # Check if problem implies integer answer (e.g., number of people, whole items)
            rounding_check = await self.generate(
                instruction=f"""
                Does the problem context require an integer answer? (e.g., count of people, phones, whole items)
                If yes, round {final_answer} to nearest integer. If no, keep as decimal.
                Return ONLY the final number.
                """,
                context=""
            )
            try:
                final_answer = float(rounding_check.strip())
                if final_answer == int(final_answer):
                    final_answer = int(final_answer)
            except:
                pass  # Keep original if parsing fails

        return str(final_answer)