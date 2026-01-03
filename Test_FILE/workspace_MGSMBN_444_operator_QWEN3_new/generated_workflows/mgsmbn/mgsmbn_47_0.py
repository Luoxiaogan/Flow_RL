# Workflow ID: mgsmbn_47_0
# Benchmark: mgsmbn
# Data Indices: [45]

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

        # === STEP 1: PARALLEL DECOMPOSITION ===
        # Extract three foundational perspectives simultaneously
        entity_analysis, math_structure, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction="""Perform detailed entity and action extraction from the Bengali problem.
                Identify:
                - All actors (people, organizations)
                - All objects (items, quantities)
                - All numerical values with their semantic roles (cost, rate, percentage, count, etc.)
                - All actions (buy, pay, divide, travel, etc.) with temporal or logical order
                - Dependencies between values (e.g., "10% of total cost")
                Format as structured bullet points with clear labels.
                Example: 
                - Actor: জেনেট
                - Object: ব্রোচ
                - Value: 500 (material cost)
                - Value: 800 (labor cost)
                - Action: Pay material cost → Pay labor cost → Pay insurance (10% of sum)
                """,
                context=""
            ),
            self.generate(
                instruction="""Analyze the mathematical structure of the problem.
                Identify:
                - Type of problem (sequential, proportional, distribution, comparison, rate, etc.)
                - Required operations (add, subtract, multiply, divide, percentage, fraction, etc.)
                - Order of operations (chronological or logical dependency)
                - Unknown variable to solve for
                - Any hidden steps or implicit calculations
                Present as a numbered sequence of mathematical steps with justifications.
                Example:
                1. Calculate total base cost: 500 + 800 = 1300 (material + labor)
                2. Calculate insurance: 10% of 1300 = 130
                3. Total payment: 1300 + 130 = 1430
                """,
                context=""
            ),
            self.generate(
                instruction="""Identify all constraints, units, and real-world boundaries.
                Consider:
                - Units of measurement (টাকা, ঘণ্টা, কিমি, জিনিস, etc.)
                - Unit conversions required
                - Constraints (non-negative, integer-only, upper/lower bounds)
                - Contextual sanity checks (e.g., can't have negative money)
                - Rounding requirements (money to 2 decimals, people to integers)
                Format as a checklist with explicit rules.
                Example:
                - [x] All values in টাকা (no conversion needed)
                - [x] Final answer must be non-negative
                - [x] Insurance is percentage of sum, not individual components
                - [x] Answer should be integer (no fractional currency mentioned)
                """,
                context=""
            )
        )

        # === STEP 2: SYNTHESIZE INTO UNIFIED MODEL ===
        problem_model = await self.generate(
            instruction=f"""Synthesize the three analyses into a single, coherent problem model.
            Combine:
            - Entities and actions from entity_analysis
            - Mathematical steps from math_structure
            - Constraints and units from constraint_analysis
            
            Create a unified specification that includes:
            1. Problem type classification
            2. Complete sequence of operations with dependencies
            3. All constraints and unit requirements
            4. Explicit formula or algorithm to compute answer
            
            Format as a structured JSON-like outline (without actual JSON syntax).
            """,
            context=f"ENTITY ANALYSIS:
{entity_analysis}

MATHEMATICAL STRUCTURE:
{math_structure}

CONSTRAINTS:
{constraint_analysis}"
        )

        # === STEP 3: PARALLEL SOLUTION GENERATION ===
        # Generate 2 distinct solution approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a detailed step-by-step solution using ALGEBRAIC modeling.
                Based on the problem model:
                {problem_model}
                
                Steps:
                1. Define variables for unknowns
                2. Write equations based on relationships
                3. Solve equations systematically
                4. Substitute known values
                5. Compute final answer
                6. Verify against constraints
                
                Show ALL intermediate calculations and reasoning.
                """,
                context=problem_model
            ),
            self.generate(
                instruction=f"""Generate a detailed step-by-step solution using ARITHMETIC SEQUENCING.
                Based on the problem model:
                {problem_model}
                
                Steps:
                1. Follow chronological or logical order of events
                2. Compute each step numerically
                3. Track units at each step
                4. Apply percentages/fractions at correct points
                5. Accumulate final result
                6. Validate against constraints
                
                Show ALL intermediate values and unit tracking.
                """,
                context=problem_model
            )
        )

        # === STEP 4: ENSEMBLE BEST SOLUTION ===
        final_solution = await self.ensemble(
            instruction="""Select the best solution or synthesize a hybrid solution.
            Criteria:
            - Completeness: Does it account for all entities, actions, and constraints?
            - Correctness: Are mathematical operations applied in right order?
            - Unit consistency: Are units tracked and converted properly?
            - Constraint adherence: Does it respect real-world boundaries?
            - Clarity: Is reasoning traceable and justifiable?
            
            If both solutions are valid but differ, identify why and merge the correct components.
            If one is clearly superior, select it and explain why.
            Output ONLY the final numerical answer in the format: 
            [answer]
            """,
            contexts_list=solution_attempts
        )

        # === STEP 5: VALIDATION LOOP (max 2 iterations) ===
        answer = final_solution.strip()
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Validate the answer against the original problem.
                Answer to validate: {answer}
                
                Check:
                1. Does this answer satisfy all conditions in the original Bengali problem?
                2. Are all numerical relationships correctly modeled?
                3. Are units and constraints respected?
                4. Is there any arithmetic error?
                5. Does the answer make real-world sense?
                
                If valid, respond with "VALID: [answer]".
                If invalid, respond with "INVALID: [detailed reason]".
                """,
                context=final_solution
            )
            
            if "VALID:" in validation:
                answer = validation.split("VALID:")[1].strip()
                break
            else:
                # Revise and regenerate
                revised_model = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    Validation feedback: {validation}
                    
                    Correct the errors while preserving correct components.
                    Ensure all constraints and dependencies are respected.
                    Show corrected step-by-step reasoning.
                    """,
                    context=final_solution
                )
                
                # Regenerate answer from revised model
                answer_attempt = await self.generate(
                    instruction="""Extract ONLY the final numerical answer from the revised solution.
                    Format: [answer]
                    """,
                    context=revised_model
                )
                answer = answer_attempt.strip()
                final_solution = revised_model

        # === STEP 6: FINAL SANITIZATION ===
        # Extract just the number (handle cases where answer is wrapped in text)
        match = re.search(r'[\d,]+\.?\d*', answer.replace(',', ''))
        if match:
            final_answer = match.group(0)
            # Convert to float then to int if whole number
            num = float(final_answer)
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        else:
            # Fallback: return as-is if no number found (shouldn't happen)
            return answer