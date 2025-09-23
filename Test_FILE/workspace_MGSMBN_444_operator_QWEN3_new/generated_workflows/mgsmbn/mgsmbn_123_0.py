# Workflow ID: mgsmbn_123_0
# Benchmark: mgsmbn
# Data Indices: [15, 55]

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

        # PHASE 1: SEMANTIC DECOMPOSITION (Parallel Multi-Perspective Extraction)
        decomposition_instructions = [
            """Analyze the Bengali problem from a MATHEMATICAL STRUCTURE perspective:
            - Identify all numerical values and their roles (constants, variables, targets)
            - Map relationships between quantities (ratios, differences, totals, rates)
            - Classify the core mathematical operation type (arithmetic, proportional, algebraic, etc.)
            - Note any implicit constraints or hidden steps
            Format output as structured bullet points.""",
            
            """Analyze the Bengali problem from a LINGUISTIC CUES perspective:
            - Extract key verbs and their mathematical implications (increase, decrease, distribute, compare, etc.)
            - Identify temporal or conditional phrases that affect operation order
            - Note Bengali-specific mathematical terminology and their standard interpretations
            - Flag any ambiguous phrasings that might have multiple interpretations
            Format output as annotated text with explanations.""",
            
            """Analyze the Bengali problem from a REAL-WORLD CONTEXT perspective:
            - Identify physical entities (people, objects, units) and their realistic constraints
            - Note any domain-specific assumptions (e.g., currency rounding, whole number requirements)
            - Highlight contextual boundaries (non-negative values, maximum/minimum limits)
            - Suggest plausibility checks for final answer
            Format output as scenario description with constraint annotations."""
        ]

        decomposition_results = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in decomposition_instructions]
        )

        # Synthesize decompositions into unified problem representation
        unified_representation = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a single coherent problem representation:
            - Combine mathematical structure, linguistic cues, and real-world constraints
            - Resolve any conflicts between perspectives by prioritizing mathematical consistency
            - Preserve all critical details needed for solution generation
            - Format as: Problem Type: [type], Knowns: [list], Unknowns: [list], Constraints: [list], Steps: [estimated count]""",
            contexts_list=decomposition_results
        )

        # PHASE 2: STRATEGY GENERATION (Parallel Solution Path Creation)
        strategy_instructions = [
            """Generate a DETAILED STEP-BY-STEP SOLUTION STRATEGY using ALGEBRAIC APPROACH:
            - Define variables for unknowns
            - Write equations based on relationships
            - Solve systematically with intermediate calculations
            - Include unit tracking at each step
            - Format as numbered steps with justifications.""",
            
            """Generate a DETAILED STEP-BY-STEP SOLUTION STRATEGY using PROPORTIONAL REASONING:
            - Identify ratios, rates, or scaling factors
            - Set up proportional relationships
            - Solve through cross-multiplication or unit rate methods
            - Include verification steps
            - Format as numbered steps with justifications.""",
            
            """Generate a DETAILED STEP-BY-STEP SOLUTION STRATEGY using ARITHMETIC SEQUENCING:
            - Break problem into chronological or logical sequence of operations
            - Perform calculations in required order
            - Track intermediate results and units
            - Include sanity checks after each major step
            - Format as numbered steps with justifications."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=unified_representation) for instr in strategy_instructions]
        )

        # PHASE 3: EXECUTION WITH VALIDATION (Iterative Refinement)
        validated_solutions = []
        
        for i, strategy in enumerate(strategy_attempts):
            current_solution = strategy
            validation_failed = False
            
            for validation_round in range(3):  # Max 3 revision attempts per strategy
                # Validate current solution
                validation = await self.generate(
                    instruction=f"""CRITICALLY VALIDATE this solution attempt:
                    - Check unit consistency at each step
                    - Verify mathematical operations are correct
                    - Ensure answer respects real-world constraints (non-negative, whole numbers if required, etc.)
                    - Confirm final answer format matches problem requirements
                    - Identify any logical gaps or calculation errors
                    If valid, respond with 'VALID: [confirmation]'. If invalid, respond with 'INVALID: [specific issues]'""",
                    context=current_solution
                )
                
                if "VALID:" in validation:
                    validated_solutions.append(current_solution)
                    break
                elif "INVALID:" in validation and validation_round < 2:  # Only revise if not last round
                    current_solution = await self.revise(
                        instruction=f"""REVISE the solution to fix these issues: {validation}
                        - Maintain the original strategy approach
                        - Correct only the identified errors
                        - Preserve correct parts of the solution
                        - Add explicit unit tracking if missing
                        - Ensure intermediate steps are clearly shown""",
                        context=current_solution
                    )
                else:
                    # Final validation failed - abandon this strategy
                    validation_failed = True
                    break
            
            if not validation_failed and "VALID:" in validation:
                validated_solutions.append(current_solution)

        # PHASE 4: SYNTHESIS AND SELECTION
        if not validated_solutions:
            # Fallback: Generate one comprehensive solution
            final_answer_attempt = await self.generate(
                instruction="""Generate a comprehensive solution considering all previous analyses:
                - Use the most reliable mathematical approach
                - Show all steps clearly
                - Include unit tracking
                - Verify against real-world constraints
                - Output final answer as: FINAL_ANSWER: [number]""",
                context=unified_representation
            )
        else:
            final_answer_attempt = await self.ensemble(
                instruction="""SELECT the best solution from the validated candidates:
                - Compare mathematical correctness first
                - Then evaluate clarity and completeness of steps
                - Prefer solutions that best handle real-world constraints
                - Extract the final numerical answer from the chosen solution
                - Output ONLY the final numerical answer as: FINAL_ANSWER: [number]""",
                contexts_list=validated_solutions
            )

        # PHASE 5: META-VALIDATION (Final Quality Check)
        final_validation = await self.generate(
            instruction="""Perform FINAL VALIDATION as a Bengali elementary math teacher:
            - Does the solution correctly interpret the Bengali problem?
            - Are all steps appropriate for elementary level?
            - Is the final answer format correct (single numerical value)?
            - Does it handle any rounding or unit conversion as specified?
            - If any issues, suggest correction. Otherwise, confirm with 'APPROVED'""",
            context=final_answer_attempt
        )

        if "APPROVED" not in final_validation:
            # One last revision if validation fails
            final_answer_attempt = await self.revise(
                instruction=f"""Apply these final corrections: {final_validation}
                - Keep solution structure intact
                - Only modify what's necessary
                - Ensure final output is: FINAL_ANSWER: [number]""",
                context=final_answer_attempt
            )

        # Extract final numerical answer
        answer_match = re.search(r'FINAL_ANSWER:\s*([\-]?\d+\.?\d*)', final_answer_attempt)
        if answer_match:
            final_answer = answer_match.group(1)
            # Convert to int if whole number, otherwise float
            if '.' in final_answer:
                return float(final_answer)
            else:
                return int(final_answer)
        else:
            # Fallback extraction if formatting failed
            numbers = re.findall(r'[+-]?\d+\.?\d*', final_answer_attempt)
            if numbers:
                answer = numbers[-1]  # Last number is likely the answer
                return float(answer) if '.' in answer else int(answer)
            else:
                return 0  # Ultimate fallback