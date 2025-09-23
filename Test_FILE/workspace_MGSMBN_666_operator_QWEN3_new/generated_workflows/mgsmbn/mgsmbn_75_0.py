# Workflow ID: mgsmbn_75_0
# Benchmark: mgsmbn
# Data Indices: [19]

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

        # PHASE 1: Decompose the problem into structured subproblems
        decomposition_instruction = """
        Break down this Bengali math word problem into atomic, solvable subproblems. For each subproblem:
        - Identify named entities (items, people, units)
        - Extract all numerical values and their semantic roles (price, quantity, total, unknown)
        - Define mathematical relationships (e.g., 'cost = price × quantity')
        - Isolate the primary unknown to solve for
        - Establish dependencies (which subproblems must be solved before others)
        Format as a numbered list of dictionaries with keys: id, description, dependencies.
        """
        decomposition = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: Classify problem archetype to guide solution strategy
        archetype_instruction = f"""
        Based on the decomposition:
        {decomposition}

        Classify this problem into one of these archetypes:
        1. Sequential Operations (e.g., spending then calculating remainder)
        2. Rate Problems (speed/time, work rate, unit price scaling)
        3. Proportional Reasoning (ratios, percentages, fractions)
        4. Distribution/Division (equal sharing, remainders)
        5. Comparison Problems (differences, "how many more")
        6. Multi-entity Tracking (multiple agents with different quantities)

        For each archetype, explain why it fits or doesn't fit.
        Then, select the single best-fitting archetype and justify your choice.
        Finally, outline the mathematical strategy this archetype implies (e.g., "Set up equation with unknown variable", "Use proportion formula", etc.).
        """
        archetype_analysis = await self.generate(
            instruction=archetype_instruction,
            context=""
        )

        # PHASE 3: Generate three parallel solution attempts using different reasoning lenses
        algebraic_instruction = f"""
        Solve using ALGEBRAIC REASONING:
        - Define a variable for the unknown quantity
        - Translate the problem into one or more equations based on the decomposition
        - Show step-by-step algebraic manipulation
        - Solve for the variable
        - State the final answer clearly

        Use the decomposition and archetype analysis as guides:
        Decomposition: {decomposition}
        Archetype: {archetype_analysis}
        """
        
        arithmetic_instruction = f"""
        Solve using ARITHMETIC REASONING:
        - Perform calculations step by step in chronological/logical order
        - Show intermediate results with units
        - Track cumulative totals or running balances as needed
        - Clearly indicate which operation (add, subtract, multiply, divide) is used at each step
        - State the final answer clearly

        Use the decomposition and archetype analysis as guides:
        Decomposition: {decomposition}
        Archetype: {archetype_analysis}
        """
        
        unit_tracking_instruction = f"""
        Solve using UNIT-TRACKING REASONING:
        - Write every quantity with its unit (টাকা, ঘণ্টা, জিনিস, etc.)
        - Ensure dimensional consistency at every operation (e.g., টাকা × জিনিস = টাকা, not ঘণ্টা)
        - Cancel or convert units explicitly where needed
        - Verify that the final answer has the correct unit for the unknown
        - State the final answer clearly

        Use the decomposition and archetype analysis as guides:
        Decomposition: {decomposition}
        Archetype: {archetype_analysis}
        """

        # Run all three solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(instruction=algebraic_instruction, context=""),
            self.generate(instruction=arithmetic_instruction, context=""),
            self.generate(instruction=unit_tracking_instruction, context="")
        )

        # PHASE 4: Critique each solution attempt
        critique_instructions = [
            f"""
            CRITIQUE THIS SOLUTION:
            - Check for logical gaps or missing steps
            - Verify arithmetic accuracy (recalculate key steps)
            - Ensure unit consistency throughout
            - Confirm the answer matches the problem's unknown
            - Flag any assumptions not stated in the original problem
            - Suggest specific corrections if errors are found

            Solution to critique:
            {solution}
            """
            for solution in solution_attempts
        ]

        critiques = await asyncio.gather(
            *[self.revise(instruction=inst, context=sol) 
              for inst, sol in zip(critique_instructions, solution_attempts)]
        )

        # PHASE 5: Ensemble - Synthesize best solution from attempts and critiques
        ensemble_instruction = f"""
        You are given three solution attempts and their critiques for a Bengali math word problem.

        Your task:
        1. Compare all solutions and critiques
        2. Identify which solution is most mathematically sound, unit-consistent, and logically complete
        3. If multiple solutions are partially correct, SYNTHESIZE a hybrid solution incorporating the best elements
        4. Resolve any contradictions using the original problem as ground truth
        5. Output ONLY the final, corrected solution with clear steps and final numerical answer

        Original Problem Context:
        {self.problem_text}

        Decomposition for reference:
        {decomposition}

        Archetype Analysis:
        {archetype_analysis}
        """
        
        synthesized_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=[f"Solution: {sol}

Critique: {crit}" 
                        for sol, crit in zip(solution_attempts, critiques)]
        )

        # PHASE 6: Programmer verification - Generate and execute code to validate
        code_verification_instruction = f"""
        Generate Python code that exactly implements the mathematical steps described in the solution below.
        Requirements:
        - Use only basic arithmetic operations (+, -, *, /)
        - Include comments explaining each step
        - Print only the final numerical answer (no text)
        - Handle decimals appropriately (float if needed)
        - Validate that the code output matches the solution's stated answer

        If the code output differs from the solution, debug and correct the code OR the solution.
        You have up to 3 attempts to get matching results.

        Solution to implement:
        {synthesized_solution}
        """
        
        verified_result = await self.programmer(
            instruction=code_verification_instruction,
            context=synthesized_solution,
            max_retries=3
        )

        # PHASE 7: Final consistency and plausibility check
        plausibility_instruction = f"""
        FINAL SANITY CHECK:
        Given the original problem and the computed answer, verify:
        - The answer is a plausible real-world quantity (e.g., no negative boxes, fractional people unless specified)
        - The unit matches what was asked for (e.g., "কত বাক্স" → integer boxes)
        - The magnitude makes sense (e.g., not 1000 boxes when total money is $50)
        - No mathematical or logical contradictions remain

        If any implausibility is detected, flag it and suggest what might have gone wrong.
        Otherwise, output the numerical answer exactly as computed.

        Original Problem:
        {self.problem_text}

        Verified Result:
        {verified_result}
        """
        
        final_answer = await self.revise(
            instruction=plausibility_instruction,
            context=verified_result
        )

        # Extract numerical answer from final output (robust parsing)
        # Look for the last number in the string, handling decimals and negatives
        numbers = re.findall(r'-?\d+\.?\d*', final_answer)
        if numbers:
            return numbers[-1]  # Return the last number found (likely the final answer)
        else:
            # Fallback: return raw result if no number found (shouldn't happen)
            return final_answer.strip()