# Workflow ID: mgsmbn_104_0
# Benchmark: mgsmbn
# Data Indices: [58, 31]

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

        # Step 1: Classify problem type and extract core entities/relationships
        classification_and_extraction = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem. Your task:

1. CLASSIFY the problem type using these categories:
   - Proportional (ratios, multiples, fractions, percentages)
   - Sequential (time-ordered operations, deposits/withdrawals, step-by-step changes)
   - Distribution (sharing, division, remainders, allocations)
   - Comparison (differences, "how many more", inequalities)
   - Multi-entity (multiple actors with different quantities)
   - Rate-based (speed, work rate, unit price, slices per pie)

2. EXTRACT all mathematical entities:
   - Numbers with their units (টাকা, পাউন্ড, টুকরো, ঘণ্টা, etc.)
   - Named entities (people, objects) and their associated quantities
   - Verbs indicating operations (যোগ, বিয়োগ, গুণ, ভাগ, বেশি, কম, অর্ধেক, গুণ)
   - Comparative phrases ("অর্ধেক", "4 গুণ বেশি", "পার্থক্য")

3. IDENTIFY the target: What exactly is being asked? Extract the final question.

4. FLAG any real-world constraints:
   - Non-negative quantities (can't have negative laundry or pie slices)
   - Integer constraints (whole people, whole slices)
   - Unit consistency requirements

Output in this structured format:
CLASSIFICATION: [type1, type2, ...]
ENTITIES: 
- [Entity]: [Value] [Unit] (e.g., Sara: 400 pounds)
RELATIONSHIPS: 
- [Entity1] [operation] [Entity2] (e.g., Raymond = 0.5 * Sara)
TARGET: [exact question restated]
CONSTRAINTS: [list of constraints]

Be exhaustive. Preserve Bengali terms where meaning is critical.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Develop a STEP-BY-STEP ARITHMETIC solution:
- Start from known values
- Apply operations in narrative order
- Show intermediate results with units
- Verify each step against extracted relationships
- End with final calculation matching the target""",
            
            """Develop an ALGEBRAIC solution:
- Assign variables to unknowns
- Write equations based on extracted relationships
- Solve system of equations
- Substitute known values
- Show algebraic manipulation steps
- Verify solution satisfies all constraints""",
            
            """Develop a UNIT-TRACKING solution:
- Start with target unit
- Work backwards to known quantities
- Show dimensional analysis at each step
- Cancel units appropriately
- Verify final unit matches expected answer type
- Highlight any unit conversions needed""",
            
            """Develop an ENTITY-RELATIONSHIP solution:
- Model each entity as a node
- Model relationships as directed edges with operations
- Traverse graph from knowns to unknowns
- Show propagation of values through relationships
- Handle cycles or dependencies explicitly
- Output final value for target entity"""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification_and_extraction) 
              for instr in strategy_instructions]
        )

        # Step 3: Validate and revise each strategy
        validation_instructions = [
            f"""CRITICALLY VALIDATE this solution attempt:

1. Check MATHEMATICAL CORRECTNESS:
   - Are operations applied in correct order?
   - Are relationships from extraction step honored?
   - Are intermediate calculations accurate?

2. Check UNIT CONSISTENCY:
   - Do units propagate correctly?
   - Is final answer in expected unit?
   - Are conversions handled properly?

3. Check REAL-WORLD VALIDITY:
   - Are all quantities non-negative where required?
   - Are fractional results allowed? (e.g., people, slices)
   - Does answer make sense in context?

4. Check COMPLETENESS:
   - Does it fully answer the target question?
   - Are all given values used appropriately?
   - Are any steps skipped or assumed?

If errors found, REVISE the solution with corrections. If no errors, return 'VALID: ' followed by original.

Focus on precision. Assume nothing. Verify everything.""",
            f"""DOUBLE-CHECK this solution attempt for hidden errors:

1. Re-calculate all arithmetic manually in your reasoning
2. Verify proportional relationships (e.g., 'half of', '4 times') are correctly interpreted
3. Check that 'difference' problems compute absolute difference unless specified otherwise
4. Ensure distribution problems account for remainders correctly
5. Validate that multi-entity problems track each entity separately

If any discrepancy, revise with explicit correction. If perfect, return 'VERIFIED: ' followed by original.""",
            f"""SANITY CHECK this solution:

1. Estimate expected answer magnitude (order of magnitude)
2. Compare calculated answer to estimate
3. Check if answer is plausible in real-world context
4. Verify no division by zero or other mathematical impossibilities
5. Ensure no circular logic or self-referential assumptions

If answer fails sanity check, revise with explanation. If passes, return 'SANITY PASSED: ' followed by original."""
        ]

        # Validate each strategy with all three validation lenses
        validated_strategies = []
        for strategy in strategy_attempts:
            validations = await asyncio.gather(
                *[self.revise(instruction=instr, context=strategy) 
                  for instr in validation_instructions]
            )
            # Combine all validations into one revised strategy
            combined_validation = "\n\n".join(validations)
            final_revised = await self.revise(
                instruction="""Synthesize all validation feedback into a single, corrected solution.
If validations conflict, prioritize mathematical correctness over estimation.
Preserve the original strategy's approach but fix all identified errors.
Output only the final corrected solution with clear steps and final answer.""",
                context=f"Original Strategy:\n{strategy}\n\nValidations:\n{combined_validation}"
            )
            validated_strategies.append(final_revised)

        # Step 4: Extract numerical answers from each validated strategy
        answer_extractions = await asyncio.gather(
            *[self.generate(
                instruction="""Extract ONLY the final numerical answer from this solution.
Ignore all text, units, and explanations.
If multiple numbers appear, select the one that directly answers the target question.
Output ONLY the number, nothing else. If uncertain, output 'UNCERTAIN'.""",
                context=strategy
            ) for strategy in validated_strategies]
        )

        # Step 5: Ensemble to select or synthesize final answer
        final_answer = await self.ensemble(
            instruction="""Select the most reliable final answer from these candidates:

1. Look for consensus: Do multiple strategies agree?
2. If consensus exists, select that answer.
3. If no consensus, evaluate which strategy:
   - Best adheres to extracted relationships
   - Has most rigorous validation
   - Makes most sense in real-world context
   - Matches unit and constraint requirements
4. If still uncertain, synthesize by:
   - Taking majority vote
   - Selecting answer from most mathematically rigorous approach
   - Choosing answer that satisfies all constraints

Output ONLY the final numerical answer. No explanations. No units. Just the number.""",
            contexts_list=answer_extractions
        )

        # Step 6: Final verification with Programmer for precision
        # Clean the answer to ensure it's a valid number
        clean_answer = await self.generate(
            instruction="""Extract only the numerical value from this text.
Remove any non-numeric characters except decimal point.
If multiple numbers, take the one that answers the original question.
If no clear number, output '0'.

Examples:
'Answer: 26 slices' → '26'
'The difference is 100.5 pounds' → '100.5'
'About 30-40 items' → '0'""",
            context=final_answer
        )

        # Generate verification code
        verification_code = await self.programmer(
            instruction=f"""Write Python code to verify this answer: {clean_answer}

Based on the original problem and extracted relationships:
{classification_and_extraction}

Write code that:
1. Recreates the mathematical model from scratch
2. Computes the answer independently
3. Compares computed answer to {clean_answer}
4. Outputs 'VERIFIED' if match, 'DISCREPANCY' if not

Include all necessary calculations. Be explicit. No shortcuts.""",
            context=classification_and_extraction
        )

        # If verification fails, attempt one revision
        if "DISCREPANCY" in verification_code:
            # Go back to best individual strategy (first validated one)
            fallback_answer = await self.generate(
                instruction="""Extract final numerical answer from this solution.
Output ONLY the number. No explanations. No units.""",
                context=validated_strategies[0]  # Use first validated strategy as fallback
            )
            clean_fallback = await self.generate(
                instruction="Clean this answer to only numerical value:",
                context=fallback_answer
            )
            return clean_fallback.strip()
        else:
            return clean_answer.strip()