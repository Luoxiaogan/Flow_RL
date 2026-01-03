# Workflow ID: mgsmbn_33_0
# Benchmark: mgsmbn
# Data Indices: [173, 152]

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
        # Launch three concurrent analytical perspectives

        linguistic_extraction = asyncio.create_task(
            self.generate(
                instruction="""Thoroughly extract all quantitative and relational elements from the Bengali word problem. Structure your output as follows:
                - NUMBERS: List every numerical value with its contextual descriptor (e.g., "2000: borrowed amount in USD")
                - ENTITIES: Identify all actors, objects, or subjects (e.g., "Zenith: borrower")
                - ACTIONS: Chronological sequence of operations or events (e.g., "borrows 2000", "pays 165 monthly for 12 months")
                - RELATIONSHIPS: Explicit mathematical or logical connections (e.g., "10% extra means total repayment = 110% of principal")
                - UNITS: All measurement units and their associations (e.g., "USD", "months", "peaches per minute")
                Ensure no numerical or relational element is omitted. Format as labeled bullet points.""",
                context=""
            )
        )

        problem_classification = asyncio.create_task(
            self.generate(
                instruction="""Classify this mathematical word problem with precision:
                1. PRIMARY TYPE: Is it Sequential, Rate-Based, Proportional, Distribution, Comparison, or Multi-Entity?
                2. REQUIRED OPERATIONS: List exact arithmetic operations needed (addition, percentage, unit conversion, etc.)
                3. HIDDEN STEPS: Are there unstated intermediate calculations? (e.g., converting hours to minutes, calculating total due before repayment)
                4. ANSWER CONSTRAINTS: What real-world constraints apply? (e.g., non-negative, integer-only, unit consistency)
                5. CONFIDENCE LEVEL: How unambiguous is this classification? (High/Medium/Low)
                Output in structured JSON-like format with clear section headers.""",
                context=""
            )
        )

        constraint_harvesting = asyncio.create_task(
            self.generate(
                instruction="""Identify ALL explicit and implicit constraints that any valid solution must satisfy:
                - MATHEMATICAL: Equations or inequalities that must hold (e.g., "total repaid + remaining = total due")
                - CONTEXTUAL: Real-world limitations (e.g., "number of people must be integer", "money can't be negative")
                - UNIT-BASED: Dimensional consistency requirements (e.g., "time units must match between rate and duration")
                - BOUNDARY: Minimum/maximum possible values (e.g., "remaining amount cannot exceed original debt")
                Present as a numbered list with brief justifications for each constraint.""",
                context=""
            )
        )

        # Await all deconstruction tasks
        extraction_result, classification_result, constraint_result = await asyncio.gather(
            linguistic_extraction, problem_classification, constraint_harvesting
        )

        # === PHASE 2: PARALLEL SOLUTION GENERATION ===
        # Generate 3 solution strategies based on classification

        procedural_solution = asyncio.create_task(
            self.generate(
                instruction=f"""Solve the problem using a step-by-step procedural approach, mimicking how a careful student would work manually:
                - Start from extracted values: {extraction_result[:500]}
                - Follow chronological or logical sequence of actions
                - Show ALL intermediate calculations with units
                - Verify each step against constraints: {constraint_result[:300]}
                - Box final answer as: \\boxed{{number}}
                Explain reasoning in Bengali-friendly mathematical terms, avoiding advanced jargon.""",
                context=extraction_result
            )
        )

        algebraic_solution = asyncio.create_task(
            self.generate(
                instruction=f"""Model the problem algebraically:
                - Define variables for unknowns based on: {extraction_result[:400]}
                - Write equations representing relationships from: {constraint_result[:300]}
                - Solve systematically, showing substitutions and simplifications
                - Validate solution against problem constraints
                - Present final numerical answer as: \\boxed{{number}}
                Use clear variable names and justify each equation's origin from the problem text.""",
                context=classification_result
            )
        )

        unit_propagation_solution = asyncio.create_task(
            self.generate(
                instruction=f"""Solve by strict unit propagation and dimensional analysis:
                - Begin with given quantities and their units from: {extraction_result[:400]}
                - At each calculation step, show unit transformations explicitly
                - Cancel or convert units to ensure final answer has correct dimension
                - Cross-check with constraints: {constraint_result[:300]}
                - Final answer must include unit if applicable, then extract pure number for boxing: \\boxed{{number}}
                This method should catch unit mismatches that other approaches might miss.""",
                context=extraction_result
            )
        )

        # Await all solution attempts
        solutions = await asyncio.gather(
            procedural_solution, algebraic_solution, unit_propagation_solution
        )

        # === PHASE 3: VALIDATION-AUGMENTED ENSEMBLE ===
        # Validate each solution against constraints before synthesizing

        validation_tasks = []
        for i, solution in enumerate(solutions):
            validation_tasks.append(
                self.generate(
                    instruction=f"""CRITICAL VALIDATION CHECK:
                    Given solution attempt:
                    {solution[:800]}
                    
                    And original constraints:
                    {constraint_result[:500]}
                    
                    Answer these questions:
                    1. Does the final answer satisfy ALL mathematical constraints?
                    2. Are all intermediate steps dimensionally consistent?
                    3. Does it violate any real-world constraints (negative counts, fractional people, etc.)?
                    4. Is the numerical answer plausible given problem context?
                    5. Confidence score (0-100%) in this solution's correctness?
                    
                    If any critical violation exists, output "INVALID: [reason]". Otherwise, output "VALID: [confidence%]". Be brutally honest.""",
                    context=solution
                )
            )

        validation_results = await asyncio.gather(*validation_tasks)

        # Filter out invalid solutions
        valid_solutions = []
        valid_validation = []
        for i, (sol, val) in enumerate(zip(solutions, validation_results)):
            if "INVALID" not in val.upper():
                valid_solutions.append(sol)
                valid_validation.append(val)
            else:
                # Attempt to revise invalid solutions once
                revised = await self.revise(
                    instruction=f"""This solution was invalidated because: {val[:300]}
                    Revise it to fix the specific issues raised, while preserving correct elements.
                    Maintain step-by-step clarity and unit tracking.
                    Final answer must be numerical and boxed: \\boxed{{number}}""",
                    context=sol
                )
                # Re-validate revised solution
                revalidation = await self.generate(
                    instruction=f"""Re-validate this revised solution against constraints: {constraint_result[:500]}
                    Same criteria as before: dimensional consistency, constraint satisfaction, plausibility.
                    Output only "VALID: [confidence%]" or "INVALID: [reason]".""",
                    context=revised
                )
                if "INVALID" not in revalidation.upper():
                    valid_solutions.append(revised)
                    valid_validation.append(revalidation)

        if not valid_solutions:
            # Fallback: take highest confidence from original validations
            valid_solutions = solutions
            valid_validation = validation_results

        # Ensemble synthesis with validation-weighted selection
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the most reliable answer from these validated solutions:
            {chr(10).join([f'Solution {i+1} (Validation: {val[:100]}): {sol[:400]}' for i, (sol, val) in enumerate(zip(valid_solutions, valid_validation))])}
            
            Selection criteria:
            1. Prefer solutions with higher validation confidence scores
            2. Favor solutions that explicitly show unit consistency
            3. Choose solutions that match multiple approaches (consensus)
            4. If conflict, prefer algebraic or unit-propagation over procedural (more rigorous)
            5. Final output MUST be a single numerical value in \\boxed{{}} format
            
            Extract and output ONLY the final numerical answer as: \\boxed{{number}}""",
            contexts_list=valid_solutions
        )

        # === PHASE 4: FINAL EXTRACTION & SANITIZATION ===
        # Extract just the number from boxed answer format
        match = re.search(r'\\boxed\{([0-9.,]+)\}', final_answer)
        if match:
            clean_answer = match.group(1).replace(',', '')  # Remove commas
            return clean_answer
        else:
            # Fallback: return as-is if no box found (let grading handle it)
            return final_answer.strip()