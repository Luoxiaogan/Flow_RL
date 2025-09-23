# Workflow ID: mgsmbn_26_0
# Benchmark: mgsmbn
# Data Indices: [28]

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

        # STEP 1: CLASSIFY PROBLEM TYPE & EXTRACT ENTITIES
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali word problem and classify it by type and structure. Your analysis must include:

1. Problem Type Classification: Identify if this is a:
   - Sequential operation (events happening in order)
   - Rate problem (speed, work, unit price)
   - Proportional reasoning (ratios, percentages, fractions)
   - Distribution problem (sharing, dividing, remainders)
   - Comparison problem (differences, "how many more")
   - Multi-entity tracking (multiple people/objects with different quantities)
   - Algebraic reversal (working backwards from result)
   - Unit conversion problem

2. Entity Extraction: List all:
   - Numerical values with their units (টাকা, ঘণ্টা, জিনিস, etc.)
   - Named entities (people, objects, places)
   - Mathematical operations implied (addition, subtraction, multiplication, division)
   - Unknowns to be solved for

3. Structural Analysis: 
   - Chronological order of events (if applicable)
   - Dependencies between quantities
   - Any implicit constraints (non-negative, integer-only, real-world limits)
   - Potential ambiguities or multiple interpretations

4. Solution Strategy Recommendation:
   - What mathematical approach is most appropriate?
   - What are the critical steps needed?
   - Are there any potential pitfalls or common errors to avoid?

Format your response as a structured analysis with clear section headings.""",
            context=""
        )

        # STEP 2: CONDITIONAL DECOMPOSITION BASED ON CLASSIFICATION
        decomposition = await self.decompose(
            instruction=f"""Based on the following classification and analysis:
{classification}

Decompose this problem into a sequence of solvable subproblems. For each subproblem:

1. Assign a unique ID (e.g., "step1", "step2")
2. Provide a clear, self-contained description of what needs to be calculated
3. Specify dependencies (which other subproblems must be solved first)
4. Indicate the mathematical operation required
5. Note any unit conversions or special constraints

Ensure the decomposition follows the natural structure of the problem:
- For sequential problems: follow chronological order
- For proportional problems: identify base quantities and scaling factors
- For algebraic reversal: start from the end state and work backward
- For multi-entity problems: track each entity separately then combine

The decomposition should be granular enough that each subproblem can be solved independently once its dependencies are met.""",
            context=classification
        )

        # STEP 3: PARALLEL SOLUTION GENERATION & ADVERSARIAL VALIDATION
        # Create tasks for solving each independent subproblem
        solve_tasks = []
        validate_tasks = []
        
        for subproblem in decomposition:
            # Generate solution for this subproblem
            solve_task = self.generate(
                instruction=f"""Solve this specific subproblem from the decomposition:
Subproblem ID: {subproblem['id']}
Description: {subproblem['description']}
Dependencies: {subproblem['dependencies']}

Provide:
1. The mathematical expression or equation needed
2. Step-by-step calculation
3. Intermediate results
4. Final result with units
5. Brief justification for why this approach is correct

Be precise and show all work.""",
                context=classification
            )
            solve_tasks.append(solve_task)
            
            # Create adversarial validation task
            validate_task = self.revise(
                instruction=f"""You are a critical validator. Your job is to find errors, inconsistencies, or oversights in the following subproblem solution attempt. Be adversarial and thorough.

Subproblem: {subproblem['description']}

Check for:
1. Mathematical errors in calculation
2. Unit inconsistencies or missing conversions
3. Violation of real-world constraints (negative quantities, fractional people, etc.)
4. Logical flaws in reasoning
5. Misinterpretation of the original problem
6. Arithmetic mistakes

If you find issues, provide a corrected version. If no issues, confirm "VALID".

Be brutally honest and detailed in your critique.""",
                context=""  # Will be filled after solve_task completes
            )
            validate_tasks.append(validate_task)

        # Execute all solve tasks in parallel
        solve_results = await asyncio.gather(*solve_tasks)
        
        # Now execute validation tasks with corresponding solve results as context
        validation_results = []
        for i, validate_task in enumerate(validate_tasks):
            validation_result = await validate_task
            validation_results.append(validation_result)
        
        # STEP 4: ENSEMBLE SYNTHESIS OF VALIDATED SOLUTIONS
        synthesis = await self.ensemble(
            instruction="""Synthesize the validated subproblem solutions into a complete, coherent solution to the original problem. Your synthesis must:

1. Integrate all subproblem solutions in logical order
2. Resolve any conflicts between generator and validator outputs
3. Ensure mathematical consistency across all steps
4. Verify that the final answer satisfies all constraints from the original problem
5. Present the complete solution pathway with clear transitions between steps
6. Highlight the final numerical answer prominently

Prioritize:
- Mathematical correctness over stylistic preferences
- Unit consistency throughout
- Real-world plausibility of the answer
- Alignment with the original problem's requirements

The final output should be a polished, complete solution ready for the programmer step.""",
            contexts_list=[f"Solution: {solve_results[i]}\nValidation: {validation_results[i]}" for i in range(len(solve_results))]
        )

        # STEP 5: ITERATIVE REFINEMENT (up to 3 iterations)
        refined_solution = synthesis
        for iteration in range(3):
            refinement_check = await self.generate(
                instruction=f"""Review this solution for the original problem and determine if it requires refinement:

{refined_solution}

Check specifically for:
1. Any remaining mathematical errors
2. Unit inconsistencies
3. Logical gaps in reasoning
4. Misalignment with the original problem statement
5. Arithmetic calculation errors

If no refinements are needed, respond with "PERFECT".
If refinements are needed, provide specific instructions for improvement.""",
                context=refined_solution
            )
            
            if "PERFECT" in refinement_check.upper():
                break
            else:
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution based on this feedback:
{refinement_check}

Make only the necessary changes to fix the identified issues. Preserve correct parts of the solution.
Ensure the final answer remains clearly identifiable.""",
                    context=refined_solution
                )

        # STEP 6: PROGRAMMATIC EXECUTION
        final_answer = await self.programmer(
            instruction=f"""Generate and execute Python code that implements the exact mathematical solution described in the following validated, refined solution:

{refined_solution}

Requirements:
1. Code must implement ONLY the mathematical operations described - no new logic
2. Include all necessary calculations in sequence
3. Validate intermediate results match the described solution
4. Output only the final numerical answer (integer or decimal)
5. Handle units appropriately (convert if needed, but final answer may be unitless if specified)
6. Ensure no division by zero or other mathematical errors
7. Round to appropriate decimal places if needed

The code should be minimal and focused solely on computing the final answer from the given steps.""",
            context=refined_solution,
            max_retries=3
        )

        # Extract just the numerical answer from the programmer output
        # Look for the last number in the output (which should be the answer)
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', final_answer)
        if numbers:
            return numbers[-1]
        else:
            # Fallback: return the entire output if no number found (shouldn't happen)
            return final_answer.strip()