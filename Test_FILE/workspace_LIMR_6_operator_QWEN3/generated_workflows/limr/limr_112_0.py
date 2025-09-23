# Workflow ID: limr_112_0
# Benchmark: limr
# Data Indices: [50, 288]

import asyncio

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

        # STEP 1: Deep Problem Classification
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this mathematical problem. Analyze:
            1. Primary domain (algebra, number theory, combinatorics, geometry, probability, etc.)
            2. Solution archetype (equation solving, optimization, counting, proof, recursion, etc.)
            3. Key mathematical objects involved (integers, polynomials, geometric figures, probabilities, etc.)
            4. Constraints and boundary conditions
            5. Expected answer format and type (especially whether it's an integer 000-999)
            6. Potential solution strategies (algebraic manipulation, combinatorial counting, geometric transformation, computational enumeration, etc.)
            7. Known theorems or identities that might apply
            8. Likely pitfalls or non-obvious insights required
            Provide a comprehensive, structured analysis that will guide subsequent solution attempts.""",
            context=""
        )

        # STEP 2: Hierarchical Decomposition
        decomposition = await self.decompose(
            instruction=f"""Based on the following classification:
            {classification}
            
            Decompose this problem into a hierarchy of subproblems. Each subproblem should be:
            - Self-contained and clearly defined
            - Assigned a unique ID
            - Listed with its dependencies (other subproblem IDs it relies on)
            - Tagged with its mathematical domain and solution approach
            - Prioritized by logical order of solution
            Return a list of subproblem dictionaries with 'id', 'description', and 'dependencies' keys.""",
            context=classification
        )

        # STEP 3: Parallel Strategy Generation
        # Generate multiple solution strategies for the whole problem
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a complete solution strategy for this problem using a {approach} approach.
                Classification context: {classification}
                
                Instructions:
                - Begin with first principles
                - Show all logical steps
                - Highlight key insights or non-obvious transformations
                - If applicable, suggest computational verification points
                - Anticipate and address potential errors or edge cases
                - Conclude with the final answer format (integer 000-999)
                Be thorough, rigorous, and detailed.""",
                context=""
            ) for approach in [
                "symbolic/algebraic",
                "computational/algorithmic",
                "combinatorial/probabilistic",
                "geometric/visual"
            ]
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # STEP 4: Strategy Refinement and Verification
        refined_strategies = []
        for i, strategy in enumerate(strategy_results):
            refined = await self.revise(
                instruction=f"""Critically revise this solution strategy:
                - Verify mathematical correctness of each step
                - Check for logical gaps or unjustified assumptions
                - Ensure all constraints from the original problem are satisfied
                - Confirm the final answer is an integer between 000 and 999
                - Improve clarity and add missing justifications
                - Suggest computational verification if not already present
                - If the strategy is fundamentally flawed, explain why and suggest an alternative approach""",
                context=strategy
            )
            refined_strategies.append(refined)

        # STEP 5: Computational Verification (Parallel)
        # Extract potential computational approaches from refined strategies
        computational_tasks = []
        for strategy in refined_strategies:
            task = self.programmer(
                instruction=f"""Based on this solution strategy:
                {strategy}
                
                Generate and execute Python code to:
                - Verify the solution computationally
                - If the strategy suggests an answer, verify it by plugging back into original constraints
                - If no answer is suggested, implement a bounded search or simulation to find the solution
                - Ensure the answer is an integer between 000 and 999
                - Return the verified answer or the computationally found answer
                Include all code and output in your response.""",
                context=strategy
            )
            computational_tasks.append(task)
        
        computational_results = await asyncio.gather(*computational_tasks)

        # STEP 6: Ensemble Synthesis
        all_candidates = refined_strategies + computational_results
        final_answer = await self.ensemble(
            instruction="""Synthesize the best answer from all candidate solutions. Consider:
            1. Mathematical correctness and rigor
            2. Computational verification
            3. Consistency across multiple approaches
            4. Adherence to problem constraints
            5. Final answer format (integer 000-999)
            
            Select the most reliable answer. If multiple answers agree, prefer the one with the most thorough verification.
            If answers conflict, analyze why and select the most logically sound.
            Extract ONLY the final integer answer (000-999) and present it in the format: "ANSWER: XXX"
            where XXX is the three-digit integer (pad with leading zeros if necessary).""",
            contexts_list=all_candidates
        )

        # STEP 7: Final Extraction and Formatting
        # Extract the answer in the required format
        extracted_answer = await self.generate(
            instruction=f"""Extract the final answer from the following synthesis:
            {final_answer}
            
            Instructions:
            - The answer must be an integer between 000 and 999
            - Format it as a three-digit string with leading zeros if necessary (e.g., 5 becomes "005", 42 becomes "042")
            - If no clear answer is found, perform one final computational verification
            - Return ONLY the three-digit string, nothing else""",
            context=final_answer
        )

        # Clean and return the answer
        # Extract digits only and pad to 3 digits
        digits = re.sub(r'\D', '', extracted_answer)
        if len(digits) == 0:
            # Fallback: try to extract from any of the computational results
            for comp_result in computational_results:
                digits = re.sub(r'\D', '', comp_result)
                if len(digits) > 0:
                    break
        
        # Ensure it's 3 digits
        answer = digits.zfill(3)[-3:]
        
        return answer