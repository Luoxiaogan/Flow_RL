# Workflow ID: mgsmbn_99_0
# Benchmark: mgsmbn
# Data Indices: [27, 165]

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

        # PHASE 1: SEMANTIC DECOMPOSITION - Build layered understanding
        initial_extraction = await self.generate(
            instruction="""Perform deep semantic extraction of the Bengali word problem. Identify:
1. ENTITIES: All people, objects, or groups mentioned (e.g., টেরি, ইয়োগার্ট, পরীক্ষা)
2. QUANTITIES: All numerical values with their units (টাকা, ঘণ্টা, জিনিস, স্কোর, etc.) and what they describe
3. RELATIONSHIPS: How quantities relate (per day, total, after discount, average, etc.)
4. OPERATIONS: Implied mathematical actions (add, subtract, multiply, divide, average, etc.)
5. CONSTRAINTS: Real-world limits (no negative items, whole numbers for people, etc.)
6. GOAL: Exactly what numerical value is being asked for

Structure your response clearly with numbered sections. Be exhaustive and precise.""",
            context=""
        )

        # Enhance with constraints and dependencies
        enriched_context = await self.generate(
            instruction=f"""Given the initial extraction:
{initial_extraction}

Now deepen the analysis:
1. Identify implicit constraints not explicitly stated (e.g., scores can't exceed 100, yogurt consumption must be integer per day)
2. Map temporal or logical dependencies (what happens first, what depends on what)
3. Flag any ambiguities or missing information
4. Suggest reasonable assumptions if needed

Output in structured format with clear headings.""",
            context=initial_extraction
        )

        # PHASE 2: PARALLEL MODELING - Generate multiple solution approaches
        modeling_tasks = [
            self.generate(
                instruction=f"""Develop an ALGEBRAIC solution model:
- Define variables for unknowns
- Write equations representing relationships
- Show step-by-step algebraic manipulation
- Keep units attached to all quantities
- Output final equation to solve

Context: {enriched_context}""",
                context=enriched_context
            ),
            self.generate(
                instruction=f"""Develop a PROCEDURAL step-by-step solution:
- List actions in chronological/logical order
- Show intermediate calculations with units
- Explain why each step is performed
- Handle unit conversions explicitly
- End with final calculation

Context: {enriched_context}""",
                context=enriched_context
            ),
            self.generate(
                instruction=f"""Develop a DIMENSIONAL ANALYSIS approach:
- Track units through every operation
- Use unit cancellation to verify correctness
- Scale quantities appropriately (per item, per day, per group)
- Identify rate conversions if needed
- Show how units lead to final answer unit

Context: {enriched_context}""",
                context=enriched_context
            )
        ]

        # Run modeling in parallel
        algebraic_model, procedural_model, dimensional_model = await asyncio.gather(*modeling_tasks)

        # PHASE 3: ENSEMBLE SYNTHESIS - Merge best elements into executable plan
        synthesized_plan = await self.ensemble(
            instruction="""Synthesize the three solution approaches into one optimal executable plan:
1. Compare the algebraic, procedural, and dimensional approaches
2. Resolve contradictions by prioritizing: unit consistency > mathematical correctness > simplicity
3. Combine strongest elements from each approach
4. Output a clear, step-by-step pseudo-code plan with:
   - Step number
   - Operation description
   - Formula or calculation
   - Units at each step
   - Expected intermediate values
5. Flag any remaining uncertainties

Final output must be directly translatable to Python code.""",
            contexts_list=[algebraic_model, procedural_model, dimensional_model]
        )

        # PHASE 4: EXECUTION WITH SELF-CORRECTION - Run code with fallback revision
        final_answer = None
        last_error = None
        
        for attempt in range(3):  # Max 3 attempts
            try:
                code_result = await self.programmer(
                    instruction=f"""Generate and execute Python code based on this plan:
{synthesized_plan}

Requirements:
- Use exact arithmetic (no rounding unless specified)
- Include unit tracking in variable names (e.g., price_taka, quantity_yogurt)
- Handle edge cases (division by zero, negative results)
- Output ONLY the final numerical answer as a float or int
- If multiple answers, select the one matching the problem's goal

If error occurs, return the error message exactly.""",
                    context=synthesized_plan,
                    max_retries=1
                )
                
                # Extract numerical answer from code output
                answer_extraction = await self.summarize(
                    instruction="""Extract the final numerical answer from the following output. 
If the output contains an error message, return the exact error text.
If multiple numbers exist, select the one that answers the original question.
Ensure the answer is a single number (integer or decimal) with no units or text.
If no valid number found, return "ERROR: No numerical answer found".""",
                    context=code_result
                )
                
                # Check if we got a valid number
                if "ERROR" not in answer_extraction and "error" not in answer_extraction.lower():
                    # Validate answer makes sense
                    validation = await self.generate(
                        instruction=f"""Validate this answer: {answer_extraction}
Against original problem and constraints:
{enriched_context}

Check:
1. Is it positive? (unless context allows negative)
2. Is it reasonable magnitude? (not astronomically large/small)
3. Does it match unit expectations? (whole number for countable items?)
4. Does it satisfy all constraints?

If valid, return "VALID: [answer]". If invalid, return "INVALID: [reason]".""",
                        context=answer_extraction
                    )
                    
                    if "VALID:" in validation:
                        final_answer = validation.split("VALID:")[1].strip()
                        break
                    else:
                        last_error = f"Validation failed: {validation}"
                else:
                    last_error = answer_extraction
                    
            except Exception as e:
                last_error = f"Exception: {str(e)}"
            
            # If we're here, we need to revise and retry
            if attempt < 2:  # Don't revise on last attempt
                synthesized_plan = await self.revise(
                    instruction=f"""REVISE THE SOLUTION PLAN due to error:
{last_error}

Original context: {enriched_context}

Improvements needed:
1. Check unit consistency in all steps
2. Verify mathematical operations (especially division and averages)
3. Ensure no division by zero
4. Handle edge cases explicitly
5. Simplify complex steps if possible

Output revised plan ready for code generation.""",
                    context=synthesized_plan
                )

        # FINAL FALLBACK: If all else fails, try direct extraction from best model
        if final_answer is None:
            direct_extraction = await self.generate(
                instruction=f"""Extract the final numerical answer directly from these analyses:
Algebraic: {algebraic_model}
Procedural: {procedural_model}
Dimensional: {dimensional_model}

Choose the most consistent answer that satisfies:
- Matches problem's requested value
- Has appropriate units
- Is positive and reasonable
- Follows all constraints

Output ONLY the number, nothing else.""",
                context=f"{algebraic_model}\n\n{procedural_model}\n\n{dimensional_model}"
            )
            
            # Clean and return
            final_answer = re.sub(r'[^\d\.]', '', direct_extraction.split()[0]) if direct_extraction.strip() else "0"

        return final_answer