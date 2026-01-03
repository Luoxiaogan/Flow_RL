# Workflow ID: mbppplus_49_0
# Benchmark: mbppplus
# Data Indices: [134, 72]

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
        import json

        # Step 1: Classify the problem type and extract key constraints
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem:
            1. Categorize the problem type: Is it mathematical, bitwise, string manipulation, list/tuple transformation, or logical?
            2. Identify input/output data types and expected formats.
            3. Extract explicit and implicit constraints (e.g., edge cases, performance requirements).
            4. Determine if the problem can be decomposed into subproblems.
            5. Suggest 2-3 potential solution strategies.
            Format your response as a structured JSON with keys: 'type', 'constraints', 'strategies', 'decomposable'.""",
            context=""
        )

        # Step 2: Parallel exploration of solution strategies
        strategies = json.loads(classification).get('strategies', [])
        strategy_contexts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Develop a detailed solution approach for this strategy:
                Strategy: {strategy}
                Problem Classification: {classification}
                Include:
                - Step-by-step reasoning
                - Potential edge cases
                - Pseudocode outline
                - Required Python constructs""",
                context=""
            ) for strategy in strategies[:3]]  # Limit to top 3 strategies
        )

        # Step 3: Ensemble synthesis of best approach
        synthesized_approach = await self.ensemble(
            instruction="""Evaluate and synthesize the proposed solution strategies:
            1. Rank strategies by correctness, efficiency, and edge-case coverage.
            2. Combine the strongest elements from each approach.
            3. Produce a unified, step-by-step solution plan with explicit handling of edge cases.
            4. Specify the exact function signature and return type required.""",
            contexts_list=strategy_contexts
        )

        # Step 4: Conditional decomposition for complex problems
        if json.loads(classification).get('decomposable', False):
            subproblems = await self.decompose(
                instruction="""Break down the problem into minimal, independent subproblems:
                - Each subproblem should be solvable in isolation
                - Specify dependencies between subproblems
                - Include input/output specifications for each
                - Prioritize subproblems that handle edge cases first""",
                context=synthesized_approach
            )
            
            # Solve subproblems in dependency order
            solutions = {}
            for subproblem in sorted(subproblems, key=lambda x: len(x.get('dependencies', '').split(','))):
                dep_solutions = "\n".join([f"{dep}: {solutions.get(dep, 'Not solved yet')}" for dep in subproblem.get('dependencies', '').split(',') if dep])
                sub_solution = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    Dependencies: {dep_solutions}
                    Overall Plan: {synthesized_approach}
                    Generate executable Python code with comprehensive test cases.""",
                    context=""
                )
                solutions[subproblem['id']] = sub_solution

            # Combine subproblem solutions
            final_context = "\n".join([f"{k}: {v}" for k, v in solutions.items()])
        else:
            final_context = synthesized_approach

        # Step 5: Generate initial code solution
        code_solution = await self.programmer(
            instruction=f"""Generate production-ready Python code:
            - Follow the exact function signature specified in the problem
            - Include comprehensive edge case handling
            - Add type hints and docstrings
            - Ensure the code is efficient and readable
            - Return only the function implementation (no test cases or explanations)
            Reference Solution Plan: {final_context}""",
            context=""
        )

        # Step 6: Iterative validation and refinement
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this code solution:
                Code: {code_solution}
                Problem Requirements: {self.problem_text}
                Check for:
                1. Correctness against sample test cases
                2. Edge case handling (empty inputs, single elements, boundary values)
                3. Type consistency and return value matching
                4. Potential bugs or logical errors
                5. Code efficiency and readability
                If any issues are found, describe them specifically.""",
                context=code_solution
            )
            
            if "no issues" in validation.lower() or "correct" in validation.lower():
                break
                
            code_solution = await self.revise(
                instruction=f"""Fix all identified issues in the code:
                Validation Feedback: {validation}
                Original Requirements: {self.problem_text}
                Maintain the exact function signature and return type.
                Return only the corrected function implementation.""",
                context=code_solution
            )

        # Step 7: Final edge case probing
        edge_case_test = await self.generate(
            instruction=f"""Proactively generate 3-5 challenging edge case test scenarios:
            - Include empty inputs, extreme values, and boundary conditions
            - For each, specify expected output
            - Verify the current solution handles them correctly
            Current Solution: {code_solution}""",
            context=code_solution
        )

        # Step 8: Final synthesis and output
        final_output = await self.ensemble(
            instruction="""Produce the final answer:
            1. If the solution passes all validations, return the code exactly as is.
            2. If edge case testing revealed new issues, incorporate fixes.
            3. Ensure the output contains ONLY the function implementation with necessary imports.
            4. No explanations, no test cases, no markdown formatting.""",
            contexts_list=[code_solution, edge_case_test]
        )

        return final_output