# Workflow ID: limr_105_0
# Benchmark: limr
# Data Indices: [141, 328]

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
        import json

        # STEP 1: Problem Classification and Strategy Selection
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Classify it along the following dimensions:
            1. Primary domain: Is it geometry, number theory, combinatorics, algebra, calculus, or probability?
            2. Solution approach: Is it best solved by (a) direct computation, (b) symbolic manipulation, (c) decomposition into subproblems, or (d) creative insight/transformation?
            3. Computational feasibility: Can it be solved by brute-force enumeration or simulation? Estimate the computational complexity.
            4. Required techniques: List specific mathematical tools needed (e.g., modular arithmetic, generating functions, trigonometric identities).
            5. Answer constraints: Must the answer be an integer between 000 and 999? Are there implicit bounds?
            Provide a structured JSON response with keys: "domain", "approach", "feasibility", "techniques", "constraints".""",
            context=""
        )

        # STEP 2: Conditional Branching Based on Classification
        # Parse classification to determine strategy
        try:
            classification_data = json.loads(classification)
            approach = classification_data.get("approach", "").lower()
            feasibility = classification_data.get("feasibility", "").lower()
        except:
            # Fallback: treat as symbolic/decomposition problem
            approach = "symbolic"
            feasibility = "unknown"

        # STEP 3: Parallel Strategy Exploration
        strategy_tasks = []

        # Always generate a decomposition path (robust fallback)
        decomposition_strategy = asyncio.create_task(
            self.generate(
                instruction=f"""Based on the problem classification: {classification}
                Systematically decompose the problem into 3-5 manageable subproblems. For each subproblem:
                - State what needs to be solved
                - Identify dependencies on other subproblems
                - Suggest the mathematical technique to apply
                - Estimate difficulty (low/medium/high)
                Format as numbered list with clear subproblem descriptions.""",
                context=""
            )
        )
        strategy_tasks.append(decomposition_strategy)

        # Generate computational strategy if feasible
        if "compute" in approach or "brute" in feasibility or "enumeration" in feasibility:
            computational_strategy = asyncio.create_task(
                self.generate(
                    instruction=f"""Given this problem's computational feasibility: {feasibility}
                    Design a precise algorithm to solve it computationally. Specify:
                    - Variables and their ranges
                    - Looping or recursive structure
                    - Success condition (what constitutes a valid solution)
                    - Edge cases to handle
                    - Expected output format (must be integer 000-999)
                    Then, generate Python code that implements this algorithm, with detailed comments explaining each step.
                    The code must be self-contained and handle all edge cases.""",
                    context=""
                )
            )
            strategy_tasks.append(computational_strategy)

        # Generate symbolic/analytical strategy
        symbolic_strategy = asyncio.create_task(
            self.generate(
                instruction=f"""Based on problem classification: {classification}
                Develop a step-by-step symbolic solution. For each step:
                - State the mathematical operation or theorem applied
                - Show the transformation explicitly
                - Justify why this step is valid
                - Check for potential errors or assumptions
                Focus on algebraic manipulation, identity application, or logical deduction as appropriate.
                The final step must yield an integer between 000 and 999.""",
                context=""
            )
        )
        strategy_tasks.append(symbolic_strategy)

        # Execute all strategies in parallel
        strategy_results = await asyncio.gather(*strategy_tasks, return_exceptions=True)

        # Filter out any failed strategies
        valid_strategies = []
        for result in strategy_results:
            if isinstance(result, Exception):
                continue
            if isinstance(result, str) and len(result.strip()) > 50:  # Non-trivial response
                valid_strategies.append(result)

        # STEP 4: Ensemble Synthesis of Strategies
        if len(valid_strategies) > 1:
            synthesized_solution = await self.ensemble(
                instruction="""You are given multiple solution strategies for the same mathematical problem. Your task:
                1. Evaluate each strategy for correctness, completeness, and efficiency.
                2. Identify which strategy is most likely to yield the correct integer answer (000-999).
                3. If strategies conflict, determine which has the strongest logical foundation.
                4. Synthesize the best elements from multiple strategies if they are complementary.
                5. Output the final answer as a single integer between 000 and 999, with a brief justification.
                Format: "ANSWER: XXX" where XXX is the three-digit integer, followed by justification.""",
                contexts_list=valid_strategies
            )
        else:
            synthesized_solution = valid_strategies[0] if valid_strategies else ""

        # STEP 5: Validation and Refinement Loop
        final_answer = synthesized_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Critically validate this solution: {final_answer}
                Check for:
                1. Mathematical correctness: Are all steps logically sound?
                2. Computational accuracy: If code was generated, does it handle edge cases?
                3. Answer format: Is the final answer an integer between 000 and 999?
                4. Consistency: Does it match the problem's constraints and initial conditions?
                If any issues are found, explain them specifically. If no issues, respond "VALID". Otherwise, list all errors.""",
                context=final_answer
            )

            if "VALID" in validation.upper() and "ERROR" not in validation.upper() and "INCORRECT" not in validation.upper():
                break
            else:
                # Revise based on validation feedback
                final_answer = await self.revise(
                    instruction=f"""Revise the solution based on this validation feedback: {validation}
                    Specifically:
                    - Correct any mathematical errors
                    - Fix computational edge cases
                    - Ensure final answer is integer 000-999
                    - Improve clarity of reasoning
                    Maintain all correct elements while addressing the identified issues.""",
                    context=final_answer
                )

        # STEP 6: Final Answer Extraction and Formatting
        final_extraction = await self.generate(
            instruction=f"""Extract the final numerical answer from this solution: {final_answer}
            The answer must be an integer between 000 and 999.
            If multiple numbers are present, select the one that is the final answer to the original problem.
            If no valid answer is found, return "000".
            Output ONLY the three-digit number, zero-padded if necessary (e.g., "042" not "42").""",
            context=final_answer
        )

        # Ensure proper formatting
        import re
        match = re.search(r'\b(\d{1,3})\b', final_extraction)
        if match:
            answer = match.group(1).zfill(3)  # Zero-pad to 3 digits
            if int(answer) > 999:
                answer = "999"  # Clamp to maximum allowed value
        else:
            answer = "000"  # Default fallback

        return answer