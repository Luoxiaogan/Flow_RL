# Workflow ID: mbppplus_58_0
# Benchmark: mbppplus
# Data Indices: [0, 321]

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

        # Step 1: Classify problem and extract key requirements
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:

            1. Classify the problem type: Is it algorithmic (DP, greedy, etc.), data manipulation, mathematical, or logical?
            2. Identify the core task: What exactly needs to be computed or transformed?
            3. Extract edge cases: Are there mentions of empty inputs, single elements, negatives, duplicates, or boundary conditions?
            4. Determine return type: Should it return int, tuple, list, set, etc.?
            5. Note any constraints: Time complexity, space complexity, or specific algorithm requirements.
            6. Identify sample inputs/outputs if provided.

            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Parallel strategy - Direct vs Decomposed approach
        direct_task = self.programmer(
            instruction=f"""Implement a Python solution for this problem:

            Problem Classification: {classification}

            Requirements:
            - Handle all edge cases mentioned in the analysis.
            - Match the exact function signature and return type.
            - Include necessary imports.
            - Write clean, efficient code.
            - Return ONLY the function implementation (no explanations).

            Original problem context is available internally.""",
            context=classification
        )

        # Decomposed approach
        decomposition = await self.decompose(
            instruction=f"""Break this problem into minimal, executable subproblems:

            Problem Classification: {classification}

            Guidelines:
            - Each subproblem should be a concrete, code-implementable step.
            - Specify dependencies between subproblems (e.g., "step2 depends on step1").
            - Focus on algorithmic steps, not high-level descriptions.
            - Include initialization, computation, and result extraction steps.

            Example subproblem: "Initialize DP array of size n with 1s" (depends on: none)
            Example subproblem: "For each i, update DP[i] based on previous values" (depends on: step1)""",
            context=classification
        )

        # Solve subproblems in dependency order (simplified: assume order is correct)
        subproblem_solutions = []
        for subproblem in decomposition:
            # Revise subproblem into code-ready spec
            code_spec = await self.revise(
                instruction="""Transform this subproblem description into a precise, executable code specification:

                - Be explicit about variables, loops, conditions.
                - Include initialization if needed.
                - Specify input/output for this step.
                - Use Python-like pseudocode if helpful.

                Example input: "Initialize DP array"
                Example output: "Create a list 'dp' of length n, initialized to 1: dp = [1] * n" """,
                context=subproblem['description']
            )
            
            # Solve with programmer
            solution = await self.programmer(
                instruction=f"""Implement this subproblem as Python code:

                Subproblem: {subproblem['description']}
                Code Spec: {code_spec}

                Requirements:
                - Return only the code snippet for this step.
                - Assume necessary variables are defined.
                - No function definitions unless required.""",
                context=code_spec
            )
            subproblem_solutions.append(solution)

        # Assemble decomposed solution
        assembly_context = "\n\n".join([
            f"Subproblem {i+1}: {sp['description']}\nSolution: {sol}"
            for i, (sp, sol) in enumerate(zip(decomposition, subproblem_solutions))
        ])

        assembled_solution = await self.generate(
            instruction=f"""Assemble these subproblem solutions into a complete Python function:

            {assembly_context}

            Requirements:
            - Use the exact function signature from the problem.
            - Include all necessary imports.
            - Handle edge cases identified in classification.
            - Return ONLY the function implementation (no explanations).
            - Ensure proper variable scoping and initialization.""",
            context=assembly_context
        )

        # Step 3: Ensemble - choose between direct and decomposed
        solutions_list = [direct_task, assembled_solution]
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:

            1. Correctness: Does it handle edge cases and match return type?
            2. Clarity: Is the code readable and well-structured?
            3. Completeness: Does it include all necessary parts (imports, function signature)?
            4. Robustness: Does it gracefully handle invalid inputs?

            Return ONLY the selected Python function implementation (no explanations).""",
            contexts_list=solutions_list
        )

        # Step 4: Final refinement - extract clean code
        clean_code = await self.revise(
            instruction="""Extract ONLY the Python function implementation:

            - Remove any markdown, explanations, or extra text.
            - Ensure exact function signature.
            - Include necessary imports at top.
            - Preserve all logic and edge case handling.
            - Return pure Python code ready for execution.""",
            context=final_solution
        )

        return clean_code