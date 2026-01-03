# Workflow ID: limr_19_0
# Benchmark: limr
# Data Indices: [336, 233]

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

        # Step 1: Meta-classification - Understand the problem's nature
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem:
            1. Identify the primary mathematical domain (geometry, number theory, combinatorics, algebra, etc.)
            2. List all key entities: numbers, variables, geometric objects, constraints
            3. Determine the solution type: proof, computation, optimization, counting, etc.
            4. Hypothesize 3 distinct solution strategies with brief rationale for each
            5. Flag any potential pitfalls or non-obvious insights required
            6. Estimate the number of logical steps required
            Format as a structured report with clear section headers.""",
            context=""
        )

        # Step 2: Parallel strategy exploration - Generate 3 distinct solution approaches
        strategy_instructions = [
            """Develop a detailed solution approach using [STRATEGY 1] perspective.
            - Break into clear, sequential steps
            - Identify key equations, theorems, or transformations needed
            - Anticipate computational or logical challenges
            - Specify what final computation or proof structure is required
            Base your approach on the classification: """ + classification,
            
            """Develop a detailed solution approach using [STRATEGY 2] perspective.
            - Break into clear, sequential steps
            - Identify key equations, theorems, or transformations needed
            - Anticipate computational or logical challenges
            - Specify what final computation or proof structure is required
            Base your approach on the classification: """ + classification,
            
            """Develop a detailed solution approach using [STRATEGY 3] perspective.
            - Break into clear, sequential steps
            - Identify key equations, theorems, or transformations needed
            - Anticipate computational or logical challenges
            - Specify what final computation or proof structure is required
            Base your approach on the classification: """ + classification
        ]

        # Extract strategy names from classification for dynamic instruction building
        strategy_names = await self.generate(
            instruction="""From the classification report below, extract exactly 3 strategy names mentioned.
            Return ONLY the three strategy names, one per line, nothing else.
            Classification: """ + classification,
            context=""
        )
        strategy_list = [s.strip() for s in strategy_names.strip().split('\n') if s.strip()][:3]
        
        # Dynamically build strategy-specific instructions
        for i, strategy in enumerate(strategy_list):
            strategy_instructions[i] = strategy_instructions[i].replace("[STRATEGY 1]", strategy) if i == 0 else strategy_instructions[i].replace("[STRATEGY 1]", "")
            strategy_instructions[i] = strategy_instructions[i].replace("[STRATEGY 2]", strategy) if i == 1 else strategy_instructions[i].replace("[STRATEGY 2]", "")
            strategy_instructions[i] = strategy_instructions[i].replace("[STRATEGY 3]", strategy) if i == 2 else strategy_instructions[i].replace("[STRATEGY 3]", "")

        # Execute parallel strategy development
        strategy_attempts = await asyncio.gather(
            self.generate(instruction=strategy_instructions[0], context=""),
            self.generate(instruction=strategy_instructions[1], context=""),
            self.generate(instruction=strategy_instructions[2], context="")
        )

        # Step 3: Adversarial revision - Stress test each strategy
        revised_strategies = []
        for i, attempt in enumerate(strategy_attempts):
            revised = await self.revise(
                instruction=f"""Critically evaluate this solution strategy:
                - Assume it contains at least one significant error
                - Identify the most likely flaw in logic, computation, or assumptions
                - Verify dimensional consistency, boundary conditions, and edge cases
                - Suggest specific corrections or alternative approaches for weak points
                - Preserve the core insight while fixing vulnerabilities
                Strategy to critique: """,
                context=attempt
            )
            revised_strategies.append(revised)

        # Step 4: Synthesis - Combine the strongest elements
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a unified solution by combining the strongest elements from all revised strategies:
            - Extract correct setup and framing from the most coherent approach
            - Incorporate accurate computations or logical steps from others
            - Resolve contradictions by selecting the most mathematically sound option
            - Ensure all steps are justified and no gaps remain
            - Produce a complete, step-by-step solution that would earn full credit
            - End with a clearly boxed final answer""",
            contexts_list=revised_strategies
        )

        # Step 5: Computational verification (if needed)
        # Check if solution contains computable expressions that need verification
        needs_computation = await self.generate(
            instruction="""Determine if the solution below requires computational verification:
            - Does it contain summations, products, or expressions that need numerical evaluation?
            - Are there modular arithmetic or large number computations?
            - Would code execution help verify the final answer?
            Return ONLY 'YES' or 'NO'.""",
            context=synthesized_solution
        )

        final_solution = synthesized_solution
        if "YES" in needs_computation.upper():
            computation_result = await self.programmer(
                instruction="""Write Python code to compute the final numerical answer from this solution.
                - Extract the exact mathematical expression that needs evaluation
                - Handle large numbers, modular arithmetic, or precision issues appropriately
                - Output only the integer result, no explanations
                - Ensure result is between 0 and 999
                Solution: """ + synthesized_solution,
                context=synthesized_solution
            )
            # Integrate computation result back into solution
            final_solution = await self.revise(
                instruction=f"""Update the solution with the computed result: {computation_result}
                - Replace any symbolic expressions with the computed integer
                - Ensure the final answer is clearly stated as a three-digit integer (000-999)
                - Maintain all reasoning steps but update the conclusion""",
                context=synthesized_solution
            )

        # Step 6: Final answer extraction and formatting
        final_answer = await self.revise(
            instruction="""Extract the final numerical answer from this solution:
            - Must be an integer between 0 and 999
            - Format as exactly three digits with leading zeros if necessary (e.g., 5 becomes 005)
            - If multiple answers, sum them modulo 1000 unless specified otherwise
            - If no clear answer, return '000'
            - Return ONLY the three-digit string, nothing else""",
            context=final_solution
        )

        # Step 7: Confidence check and iterative refinement (if needed)
        confidence_check = await self.generate(
            instruction="""Rate your confidence in this answer on a scale of 1-10:
            - 1-3: Major doubts, likely incorrect
            - 4-6: Some uncertainty, possible error
            - 7-10: High confidence, solution is robust
            Also list the top 1-3 potential sources of error if confidence < 7.
            Return format: 'CONFIDENCE: X' followed by optional error analysis.""",
            context=final_solution
        )

        if "CONFIDENCE: 1" in confidence_check or "CONFIDENCE: 2" in confidence_check or "CONFIDENCE: 3" in confidence_check:
            # Low confidence - trigger refinement loop
            for _ in range(2):  # Maximum 2 refinement iterations
                critique = await self.generate(
                    instruction="""Generate a harsh critique of this solution:
                    - What fundamental assumption might be wrong?
                    - What alternative interpretation of the problem exists?
                    - What mathematical tool was overlooked?
                    - Propose a radically different approach""",
                    context=final_solution
                )
                refined_solution = await self.revise(
                    instruction="""Completely rethink the solution based on this critique: """ + critique,
                    context=final_solution
                )
                # Re-run computation and formatting if needed
                needs_recomputation = await self.generate(
                    instruction="Does this revised solution require recomputation? YES or NO",
                    context=refined_solution
                )
                if "YES" in needs_recomputation.upper():
                    recomputation = await self.programmer(
                        instruction="Compute final answer from revised solution",
                        context=refined_solution
                    )
                    refined_solution = await self.revise(
                        instruction=f"Update with recomputed result: {recomputation}",
                        context=refined_solution
                    )
                
                new_answer = await self.revise(
                    instruction="Extract final three-digit answer",
                    context=refined_solution
                )
                final_answer = new_answer
                final_solution = refined_solution
                
                # Re-check confidence
                new_confidence = await self.generate(
                    instruction="Rate confidence in revised solution (1-10)",
                    context=final_solution
                )
                if "CONFIDENCE: 7" in new_confidence or "CONFIDENCE: 8" in new_confidence or "CONFIDENCE: 9" in new_confidence or "CONFIDENCE: 10" in new_confidence:
                    break

        return final_answer.strip()