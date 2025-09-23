# Workflow ID: mbppplus_69_0
# Benchmark: mbppplus
# Data Indices: [272, 361]

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

        # Step 1: Extract detailed functional contract
        contract = await self.generate(
            instruction="""Parse the problem text and extract the exact functional contract. Identify:
            1. Input parameters and their expected types, ranges, and constraints
            2. Output type and format requirements
            3. Edge cases explicitly mentioned or implied (empty inputs, zero, negatives, boundaries)
            4. Any constraints on algorithmic approach (recursion, iteration, etc.)
            5. Examples provided and what they imply about behavior
            Structure this as a clear, comprehensive specification that captures all requirements and edge cases.
            Think like a requirements analyst, not a coder.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this contract:
                {contract}
                
                Implement a RECURSIVE solution. Handle all edge cases explicitly. 
                Prioritize correctness over performance. Include type handling and boundary checks.
                Return only the function implementation with necessary imports.""",
                context=contract
            ),
            self.generate(
                instruction=f"""Based on this contract:
                {contract}
                
                Implement an ITERATIVE solution. Handle all edge cases explicitly.
                Optimize for efficiency and stack safety. Include type handling and boundary checks.
                Return only the function implementation with necessary imports.""",
                context=contract
            ),
            self.generate(
                instruction=f"""Based on this contract:
                {contract}
                
                Implement a MATHEMATICAL/CLOSED-FORM solution if applicable. Handle all edge cases.
                Use mathematical formulas for efficiency. Include type handling and boundary checks.
                If no closed-form exists, implement the most efficient algorithmic approach.
                Return only the function implementation with necessary imports.""",
                context=contract
            )
        )

        # Step 3: Critique each solution against the contract
        critiqued_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique this solution mercilessly against the contract:
                Contract: {contract}
                
                Check:
                1. Does it handle ALL edge cases from the contract?
                2. Does it return the exact expected type and format?
                3. Are there off-by-one errors or boundary condition failures?
                4. Is recursion depth safe for large inputs?
                5. Does it match all provided examples?
                6. Is it type-safe and defensive against invalid inputs?
                
                If any flaw is found, rewrite the solution to fix it.
                If no flaws, return it unchanged.
                Return only the corrected function implementation.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 4: Synthesize the best solution from all critiqued versions
        synthesized_solution = await self.ensemble(
            instruction="""You are given multiple correct implementations of the same function.
            Synthesize a final version that:
            1. Is maximally robust (handles edge cases most comprehensively)
            2. Is most efficient for large inputs
            3. Matches the expected return type exactly
            4. Is readable and maintainable
            5. Incorporates the best aspects of each solution
            
            If one solution is clearly superior, return it.
            If they have complementary strengths, merge them (e.g., use iterative approach but add recursion depth checks).
            Return only the final function implementation with necessary imports.""",
            contexts_list=critiqued_solutions
        )

        # Step 5: Validate with comprehensive test suite
        validated_solution = await self.programmer(
            instruction=f"""Take this solution:
            {synthesized_solution}
            
            Write and execute a comprehensive test suite that includes:
            1. All provided examples from the original problem
            2. Edge cases from the contract (empty, zero, negative, max values)
            3. Randomized inputs within valid ranges
            4. Type consistency checks
            5. Performance tests for large inputs if applicable
            
            If any tests fail, correct the code and retest.
            Return only the final, validated function implementation with necessary imports.""",
            context=synthesized_solution
        )

        # Step 6: Distill final answer (remove any test code or extra text)
        final_answer = await self.summarize(
            instruction="""Extract ONLY the function implementation from the validated code.
            Remove any test code, comments, print statements, or extra text.
            Return ONLY the function definition exactly as required:
            - Imports at top (if any)
            - Exact function signature preserved
            - No wrapping in classes or additional functions
            - Ready for direct submission
            Ensure perfect formatting and syntax.""",
            context=validated_solution
        )

        return final_answer