# Workflow ID: mbppplus_158_0
# Benchmark: mbppplus
# Data Indices: [41, 109]

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

        # Step 1: Deep problem analysis - understand structure, edge cases, and solution strategy
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem:
            1. Identify the core task: What transformation or computation is required?
            2. Examine any provided test cases to infer expected behavior, edge cases, and return type requirements.
            3. Determine the data structures involved (lists, tuples, sets, strings, etc.) and any constraints.
            4. Identify potential edge cases: empty inputs, single elements, duplicates, type boundaries.
            5. Propose a high-level solution strategy (e.g., "use set operations for deduplication", "simple indexing", "recursive processing").
            6. Assess complexity: Is this a single-step operation or does it require decomposition into subproblems?
            7. Note any ambiguities or areas requiring clarification.
            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Strategy selection - decide whether to decompose or generate directly
        strategy_decision = await self.generate(
            instruction=f"""Based on the following analysis, decide the optimal solution approach:
            {analysis}
            
            Choose one of two strategies:
            A) DIRECT: The problem can be solved with a single, straightforward implementation (e.g., indexing, simple transformation).
            B) DECOMPOSE: The problem involves multiple steps, nested structures, or complex logic requiring decomposition.
            
            Respond ONLY with 'DIRECT' or 'DECOMPOSE'.""",
            context=analysis
        )

        code_solution = None

        if "DECOMPOSE" in strategy_decision.upper():
            # Step 3a: Decompose into subproblems
            subproblems = await self.decompose(
                instruction="""Break this problem into logical subproblems that can be solved independently or sequentially.
                Each subproblem should be a clear, self-contained task that contributes to the overall solution.
                Consider data transformations, intermediate validations, and edge case handling as separate subproblems if needed.""",
                context=analysis
            )

            # Solve subproblems in parallel
            subproblem_solutions = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Solve this subproblem as part of the larger solution:
                    {sp['description']}
                    
                    Consider how this fits into the overall problem context and maintains consistency with other components.
                    Provide a clear, executable code snippet or algorithmic step.""",
                    context=analysis
                ) for sp in subproblems]
            )

            # Ensemble subproblem solutions into cohesive code
            code_solution = await self.ensemble(
                instruction="""Synthesize the following subproblem solutions into a complete, cohesive Python function:
                - Ensure proper function signature as specified in the original problem
                - Handle edge cases identified in the analysis
                - Maintain correct data types and structure
                - Include necessary imports
                - Return the exact format required (list, tuple, set, etc.)
                
                Subproblem solutions:
                """ + "\n\n".join(subproblem_solutions),
                contexts_list=subproblem_solutions
            )
        else:
            # Step 3b: Direct code generation
            code_solution = await self.programmer(
                instruction=f"""Implement a Python function that solves the problem based on this analysis:
                {analysis}
                
                Requirements:
                - Use the exact function name and parameters specified in the problem
                - Handle all edge cases mentioned in the analysis (empty inputs, single elements, etc.)
                - Return the correct data type (list, tuple, set, etc.) as demonstrated in test cases
                - Include necessary imports at the top
                - Code must be efficient and readable
                - Do not include any test cases or print statements
                - Return only the function implementation as specified in the output format
                
                If test cases were provided in the problem, ensure your implementation satisfies them.
                Consider potential edge cases even if not explicitly shown in examples.""",
                context=analysis,
                max_retries=3
            )

        # Step 4: Validation and refinement loop
        for iteration in range(2):  # Maximum 2 refinement iterations
            validation = await self.generate(
                instruction=f"""Critically evaluate this code solution for correctness:
                {code_solution}
                
                Check against:
                1. The original problem requirements
                2. Any provided test cases
                3. Edge cases identified in the analysis
                4. Return type and structure requirements
                5. Potential bugs or logical errors
                
                If the code appears correct, respond with 'VALID'.
                If improvements are needed, provide specific, actionable feedback for revision.""",
                context=code_solution
            )

            if "VALID" in validation.upper():
                break
            else:
                # Revise code based on feedback
                code_solution = await self.revise(
                    instruction=f"""Improve the code based on this feedback:
                    {validation}
                    
                    Requirements:
                    - Maintain the exact function signature
                    - Fix identified issues while preserving correct functionality
                    - Ensure edge case handling
                    - Return the implementation in the required format""",
                    context=code_solution
                )

        return code_solution