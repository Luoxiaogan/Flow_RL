# Workflow ID: limr_96_0
# Benchmark: limr
# Data Indices: [138, 105]

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

        # PHASE 1: PROBLEM CLASSIFICATION & DECOMPOSITION
        classification = await self.generate(
            instruction="""Comprehensively classify this mathematical problem:
            1. Primary domain (geometry, number theory, combinatorics, algebra, optimization, sequences)
            2. Secondary domains or cross-domain elements
            3. Required techniques (proof, calculation, transformation, induction, etc.)
            4. Expected answer format (integer, fraction, expression, etc.)
            5. Key constraints or special conditions
            6. Potential pitfalls or common mistakes
            Present as a structured, bullet-point analysis with clear headers.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into mathematically meaningful, executable subproblems:
            - Each subproblem must be atomic and solvable independently or with specified dependencies
            - Map each to a specific mathematical technique or operator (e.g., 'solve system of equations', 'apply modular inverse', 'compute geometric intersection')
            - Include verification steps where appropriate (e.g., 'verify solution satisfies original constraint')
            - Prioritize subproblems that unlock subsequent steps
            - Use the classification to guide decomposition strategy: {classification}
            Return as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=classification
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_instructions = [
            """Develop a ALGEBRAIC/COMPUTATIONAL solution strategy:
            - Translate problem into equations, variables, and constraints
            - Identify computational bottlenecks and plan precise calculations
            - Specify exact arithmetic requirements (rational, modular, etc.)
            - Outline step-by-step symbolic manipulation or algorithm""",
            
            """Develop a GEOMETRIC/VISUAL solution strategy:
            - Represent problem spatially or diagrammatically
            - Identify symmetries, invariants, or transformations
            - Use coordinate geometry, vectors, or trigonometric identities
            - Plan geometric constructions or interpretations""",
            
            """Develop a COMBINATORIAL/LOGICAL solution strategy:
            - Frame as counting, probability, or logical deduction
            - Identify combinatorial structures (permutations, partitions, graphs)
            - Apply pigeonhole, inclusion-exclusion, or recursive reasoning
            - Consider small cases or pattern recognition"""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # PHASE 3: STRATEGY EXECUTION WITH VERIFICATION LOOP
        async def execute_and_verify(strategy, strategy_name):
            for attempt in range(3):  # Max 3 revision attempts
                # Generate solution attempt
                solution_attempt = await self.generate(
                    instruction=f"""Execute this {strategy_name} strategy:
                    - Follow the plan step by step
                    - Show all intermediate calculations and reasoning
                    - Maintain mathematical rigor and precision
                    - If stuck, note the obstacle and propose workaround
                    Strategy: {strategy}""",
                    context=strategy
                )
                
                # Verify solution
                verification = await self.generate(
                    instruction=f"""Critically verify this solution attempt:
                    - Check for logical consistency and mathematical correctness
                    - Validate against original problem constraints
                    - Identify any calculation errors or flawed assumptions
                    - Assess completeness (does it answer the exact question?)
                    - If verified, output 'VERIFIED: [summary]'; else 'ERROR: [description]'
                    Solution attempt: {solution_attempt}""",
                    context=solution_attempt
                )
                
                if "VERIFIED" in verification:
                    return solution_attempt
                
                # Revise if error found
                solution_attempt = await self.revise(
                    instruction=f"""Revise the solution to fix these issues:
                    {verification}
                    - Address all identified errors
                    - Strengthen weak reasoning
                    - Recompute any suspect calculations
                    - Maintain original strategy unless fundamentally flawed""",
                    context=solution_attempt
                )
            
            return solution_attempt  # Return best attempt after 3 tries

        # Execute all strategies in parallel
        executed_strategies = await asyncio.gather(
            execute_and_verify(strategies[0], "ALGEBRAIC"),
            execute_and_verify(strategies[1], "GEOMETRIC"),
            execute_and_verify(strategies[2], "COMBINATORIAL")
        )

        # PHASE 4: SYNTHESIS & SELECTION
        synthesis = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts:
            - Compare correctness, completeness, and elegance
            - Identify consensus results or complementary insights
            - Resolve contradictions through mathematical verification
            - Select the single most reliable solution path
            - If multiple are equally valid, choose the most computationally efficient
            Output the final selected solution with clear justification.""",
            contexts_list=executed_strategies
        )

        # PHASE 5: COMPUTATIONAL EXECUTION (if needed)
        # Check if final answer requires precise computation
        needs_computation = await self.generate(
            instruction=f"""Determine if the final solution requires precise computation:
            - Are there unresolved expressions, sums, or equations?
            - Is numerical evaluation needed for final answer?
            - Would code execution reduce error risk?
            Answer 'YES' or 'NO' with brief justification.
            Solution: {synthesis}""",
            context=synthesis
        )

        if "YES" in needs_computation.upper():
            computation_result = await self.programmer(
                instruction=f"""Write and execute Python code to compute the final answer:
                - Use exact arithmetic (fractions, integers, symbolic if needed)
                - Handle edge cases and constraints from original problem
                - Output must be a single integer between 000 and 999
                - Include verification step within code if possible
                Base solution: {synthesis}""",
                context=synthesis
            )
            final_answer_source = computation_result
        else:
            final_answer_source = synthesis

        # PHASE 6: FINAL FORMATTING & VALIDATION
        formatted_answer = await self.revise(
            instruction=f"""Extract and format the final answer:
            - Must be an integer between 000 and 999
            - If answer is m/n, compute m + n and validate it's in range
            - Remove all reasoning, show only the 3-digit formatted answer
            - Pad with leading zeros if necessary (e.g., 42 → 042)
            - Verify this matches the problem's requirements
            Source: {final_answer_source}""",
            context=final_answer_source
        )

        # Extract just the 3-digit answer using regex as final safeguard
        match = re.search(r'\b(\d{3})\b', formatted_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: return first 3-digit number found
            numbers = re.findall(r'\d+', formatted_answer)
            for num in numbers:
                if len(num) <= 3:
                    return num.zfill(3)
            return "000"  # Ultimate fallback