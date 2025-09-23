# Workflow ID: mbppplus_85_0
# Benchmark: mbppplus
# Data Indices: [310, 294, 202]

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

        # Phase 1: Problem Classification and Strategy Identification
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:
            1. Classify by algorithmic paradigm: Is it optimization, dynamic programming, mathematical property, 
               search, transformation, or validation?
            2. Identify key constraints: input types, edge cases (empty, single element, negatives, duplicates), 
               performance requirements.
            3. Determine output requirements: exact signature, return type, format.
            4. Suggest 2-3 potential solution strategies with their trade-offs.
            5. What are the critical edge cases that must be handled?
            Provide structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation from Multiple Perspectives
        solution_tasks = [
            self.generate(
                instruction=f"""Develop a solution assuming this is a GREEDY/OPTIMIZATION problem:
                - Focus on locally optimal choices leading to global optimum
                - Handle edge cases explicitly: empty inputs, single elements, negatives, duplicates
                - Ensure correct return type and function signature
                - Include necessary imports inside function if needed
                Base your approach on this classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a solution assuming this is a DYNAMIC PROGRAMMING problem:
                - Define state, recurrence relation, and base cases
                - Use memoization or tabulation as appropriate
                - Handle edge cases explicitly
                - Ensure correct return type and function signature
                - Include necessary imports
                Base your approach on this classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a solution using MATHEMATICAL/FORMULA-BASED approach:
                - Look for mathematical properties, invariants, or shortcuts
                - Consider number theory, algebraic identities, or combinatorial properties
                - Handle edge cases explicitly
                - Ensure correct return type and function signature
                - Include necessary imports
                Base your approach on this classification: {classification}""",
                context=""
            )
        ]
        
        candidate_solutions = await asyncio.gather(*solution_tasks)

        # Phase 3: Ensemble Synthesis - Merge Best Elements
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions:
            1. Compare approaches for correctness, edge-case handling, and efficiency
            2. Merge robust components: take greedy's simplicity where applicable, DP's thoroughness for overlapping subproblems, 
               mathematical shortcuts for performance
            3. Ensure explicit handling of ALL edge cases identified in classification
            4. Verify function signature and return type match requirements exactly
            5. Output ONLY the final function implementation with imports, no explanations
            6. Prioritize clarity and correctness over premature optimization""",
            contexts_list=candidate_solutions
        )

        # Phase 4: Iterative Refinement with Edge-Case Validation
        current_solution = synthesized_solution
        for iteration in range(3):
            # Generate edge case critique
            edge_case_analysis = await self.generate(
                instruction=f"""Critically analyze this solution for edge case vulnerabilities:
                - Test with empty inputs, single elements, all negatives, duplicates, zeros, extreme values
                - Does it handle type mismatches or invalid inputs gracefully?
                - Are there any logical gaps in boundary conditions?
                - Suggest specific fixes for any weaknesses found
                Solution to analyze: {current_solution}""",
                context=current_solution
            )
            
            # Check if refinement is needed
            confidence_check = await self.generate(
                instruction=f"""Rate the robustness of this solution on edge cases (1-10):
                - 10: Handles all edge cases perfectly
                - 7-9: Minor issues that need fixing
                - <7: Major flaws requiring significant revision
                Justify your rating. If rating < 8, specify exactly what needs revision.
                Solution: {current_solution}
                Edge case analysis: {edge_case_analysis}""",
                context=f"{current_solution}\n\n{edge_case_analysis}"
            )
            
            if "rating" in confidence_check.lower() and any(phrase in confidence_check.lower() for phrase in ["8", "9", "10", "perfect", "robust", "handles all"]):
                break
            
            # Revise based on feedback
            current_solution = await self.revise(
                instruction=f"""Improve the solution based on this edge case analysis:
                - Fix all identified vulnerabilities
                - Maintain correct function signature and return type
                - Keep code clean and readable
                - Add necessary imports if missing
                Edge case feedback: {edge_case_analysis}
                Current solution: {current_solution}""",
                context=current_solution
            )

        # Phase 5: Final Signature and Type Enforcement
        final_solution = await self.revise(
            instruction="""Final polish:
            1. Ensure function name and parameters EXACTLY match requirements
            2. Verify return type (int, bool, list, tuple, etc.) matches test cases
            3. Include ALL necessary imports inside function if used
            4. Remove any debug prints or extra text
            5. Output ONLY the function code - no explanations, no markdown
            6. Ensure clean, PEP8-compliant formatting""",
            context=current_solution
        )

        # Extract just the function code (remove any surrounding text)
        code_match = re.search(r'