# Workflow ID: mgsmbn_48_0
# Benchmark: mgsmbn
# Data Indices: [91, 114]

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
        import json

        # === PHASE 1: PROBLEM CLASSIFICATION & DECOMPOSITION ===
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify it using this structured approach:

1. Problem Type Classification:
   - Direct Arithmetic (simple +, -, ×, ÷ with explicit numbers)
   - Proportional Reasoning (%, ratios, fractions, scaling)
   - Multi-step Sequential (requires ordered operations, e.g., buy then sell)
   - Distribution/Comparison (sharing, remainders, "how many more")
   - Rate/Time Based (speed, work rate, unit price over time)

2. Complexity Assessment:
   - Number of distinct calculation steps required (1, 2, 3+)
   - Presence of hidden intermediate steps (yes/no)
   - Unit conversions needed (yes/no + specify units)
   - Multi-entity tracking (multiple people/objects with different values)

3. Key Components Extraction:
   - List all numerical values with their contextual meaning
   - Identify the unknown being asked for
   - Note any constraints or real-world limitations

4. Solution Strategy Recommendation:
   - Suggest the most appropriate mathematical approach
   - Flag any potential pitfalls or ambiguous phrasings

Format your response as a structured report with clear section headers.""",
            context=""
        )

        # === PHASE 2: ADAPTIVE STRATEGY SELECTION ===
        # Determine if we need complex parallel processing or simple linear flow
        is_complex = any(phrase in classification.lower() for phrase in ["multi-step", "3+", "hidden", "sequential", "rate/time"])

        if is_complex:
            # === COMPLEX PATH: PARALLEL SOLUTION GENERATION ===
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate a complete solution using ALGEBRAIC MODELING approach:
                    - Define variables for unknowns
                    - Write equations based on relationships
                    - Solve step-by-step with full working
                    - Maintain unit annotations throughout
                    - Verify final answer makes real-world sense
                    Base your work on this classification: {classification}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate a complete solution using STEP-BY-STEP ARITHMETIC approach:
                    - Break into chronological/sequential steps
                    - Calculate intermediate values explicitly
                    - Show all arithmetic operations
                    - Track units and conversions
                    - Double-check each calculation
                    Base your work on this classification: {classification}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Generate a complete solution using PROPORTIONAL REASONING approach:
                    - Identify ratios, percentages, or scaling factors
                    - Set up proportions or percentage calculations
                    - Cross-multiply or use unitary method
                    - Verify proportional relationships hold
                    - Check for consistency with problem constraints
                    Base your work on this classification: {classification}""",
                    context=""
                )
            )

            # === PHASE 3: VALIDATION & ERROR DETECTION ===
            validation_results = await asyncio.gather(
                *[self.revise(
                    instruction="""Critically validate this solution:
                    - Check that all numbers match the problem statement
                    - Verify sequence of operations is logical
                    - Ensure units are consistent and properly converted
                    - Confirm no fractional people/items unless allowed
                    - Flag any arithmetic errors or logical inconsistencies
                    - Return validation as JSON: {"valid": true/false, "issues": [], "suggested_fixes": []}""",
                    context=attempt
                ) for attempt in solution_attempts]
            )

            # === PHASE 4: ERROR CORRECTION LOOP ===
            corrected_solutions = []
            for i, (attempt, validation) in enumerate(zip(solution_attempts, validation_results)):
                try:
                    # Parse validation JSON
                    val_data = json.loads(validation.replace("'", "\""))
                    if not val_data.get("valid", False):
                        # Revise based on identified issues
                        corrected = await self.revise(
                            instruction=f"""Revise this solution to fix the following issues:
                            {val_data.get('issues', [])}
                            Apply these fixes:
                            {val_data.get('suggested_fixes', [])}
                            Maintain all correct parts of the original solution.""",
                            context=attempt
                        )
                        corrected_solutions.append(corrected)
                    else:
                        corrected_solutions.append(attempt)
                except:
                    # If validation parsing fails, keep original
                    corrected_solutions.append(attempt)

            # === PHASE 5: ENSEMBLE SYNTHESIS ===
            final_answer = await self.ensemble(
                instruction="""Synthesize the final answer from these solution attempts:
                - Compare numerical results across all paths
                - Where paths disagree, identify the point of divergence
                - Select the solution whose assumptions best match the problem's explicit and implicit constraints
                - If all paths agree, return the consensus answer
                - Extract ONLY the final numerical answer as a single number (integer or decimal)
                - Do not include units or explanations in the final output""",
                contexts_list=corrected_solutions
            )

        else:
            # === SIMPLE PATH: LINEAR SOLUTION ===
            initial_solution = await self.generate(
                instruction=f"""Generate a complete solution for this problem:
                - Show all working steps clearly
                - Maintain unit consistency
                - Verify your final answer makes real-world sense
                - Double-check arithmetic
                Base your work on this classification: {classification}""",
                context=""
            )

            # Single validation
            validation = await self.revise(
                instruction="""Critically validate this solution:
                - Check that all numbers match the problem statement
                - Verify sequence of operations is logical
                - Ensure units are consistent
                - Confirm no fractional people/items unless allowed
                - Flag any arithmetic errors
                - If valid, return the solution unchanged
                - If invalid, correct the errors and return revised solution""",
                context=initial_solution
            )

            # Extract final answer
            final_answer = await self.summarize(
                instruction="""Extract the final numerical answer from this solution:
                - Return ONLY the number (integer or decimal)
                - Remove all units, explanations, and working
                - If multiple numbers exist, select the one that answers the question
                - Ensure the format matches the expected answer type""",
                context=validation
            )

        # === PHASE 6: FINAL CLEANUP & OUTPUT ===
        # Ensure output is clean numerical value
        clean_answer = await self.summarize(
            instruction="""Clean and standardize this numerical answer:
            - Remove any non-numeric characters (units, text, symbols)
            - Ensure it's a valid number (integer or decimal)
            - If it's a whole number, return as integer without decimal
            - If decimal, maintain appropriate precision
            - Return ONLY the number, nothing else""",
            context=final_answer
        )

        # Final verification - ensure it's a number
        try:
            # Try to convert to float then to int if whole number
            num = float(clean_answer.strip())
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        except:
            # Fallback: return as-is if conversion fails
            return clean_answer.strip()