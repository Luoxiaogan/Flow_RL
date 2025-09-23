# Workflow ID: mbppplus_147_0
# Benchmark: mbppplus
# Data Indices: [344, 348]

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

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its essential components:
            1. Input type and structure (e.g., list of tuples, string, number)
            2. Output type and structure (e.g., set, sorted list, count)
            3. Transformation logic (what operation needs to be performed)
            4. Edge cases to consider (empty inputs, single elements, duplicates, type boundaries)
            5. Validation criteria (what constitutes a correct solution)
            Return each as a separate subproblem with clear descriptions.""",
            context=""
        )

        # Step 2: Parallel analysis tracks
        constraint_analysis, strategy_generation, edge_case_prediction = await asyncio.gather(
            self.generate(
                instruction="""Based on the problem decomposition, extract formal constraints:
                - What are the exact input and output types?
                - Are there ordering requirements?
                - Are duplicates allowed or should be removed?
                - Are there performance or complexity constraints?
                - What Python idioms or built-ins are likely relevant?
                Format as a structured list of constraints.""",
                context=str(decomposition)
            ),
            self.generate(
                instruction="""Generate 3 distinct solution strategies for this problem:
                1. A straightforward, readable approach
                2. An optimized or clever approach using Python built-ins
                3. A defensive approach that explicitly handles edge cases
                For each, describe the core logic and why it might be suitable.""",
                context=str(decomposition)
            ),
            self.generate(
                instruction="""Predict 5 plausible test cases including edge cases:
                - Empty input
                - Single element
                - Maximum/minimum values
                - Duplicates
                - Type boundary cases
                For each, specify expected input and expected output.
                This will be used to validate the solution.""",
                context=str(decomposition)
            )
        )

        # Step 3: Synthesize into a unified specification
        specification = await self.ensemble(
            instruction="""Synthesize the constraint analysis, solution strategies, and edge cases into a single comprehensive specification for code generation:
            1. Combine the most important constraints
            2. Select the most appropriate solution strategy (or blend elements)
            3. Incorporate edge case handling requirements
            4. Define the exact function signature and return type
            5. Specify any necessary imports
            The output should be a clear, unambiguous spec that a programmer could implement directly.""",
            contexts_list=[constraint_analysis, strategy_generation, edge_case_prediction]
        )

        # Step 4: Generate initial code implementation
        initial_code = await self.programmer(
            instruction=f"""Generate a Python function that satisfies this specification:
            {specification}
            
            Requirements:
            - Use the exact function name from the problem
            - Handle all edge cases identified
            - Return the correct data type
            - Include necessary imports
            - Write clean, readable, Pythonic code
            - Do NOT include test cases or print statements""",
            context=specification,
            max_retries=2
        )

        # Step 5: Validation and revision loop
        current_code = initial_code
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Critically evaluate this code against the problem specification and predicted edge cases:
                Specification: {specification}
                
                Code to evaluate:
                {current_code}
                
                Check for:
                1. Correctness on all predicted edge cases
                2. Type consistency (input/output types)
                3. Handling of empty/single element cases
                4. Efficiency and Pythonic style
                5. Adherence to exact function signature
                
                If any issues are found, describe them specifically. If no issues, say "VALID". """,
                context=current_code
            )
            
            if "VALID" in validation_feedback.upper() and "ISSUE" not in validation_feedback.upper():
                break
                
            current_code = await self.revise(
                instruction=f"""Revise the code to fix the issues identified:
                Issues: {validation_feedback}
                
                Requirements:
                - Maintain the exact function signature
                - Fix all identified issues
                - Preserve correct behavior on edge cases
                - Keep code clean and readable""",
                context=current_code
            )

        # Step 6: Final ensemble to select best version (if we had multiple candidates)
        # In this workflow, we have one refined candidate, but we'll use ensemble to self-validate
        final_code = await self.ensemble(
            instruction="""Select the best version of the code (in this case, there's only one, but evaluate it rigorously):
            Criteria:
            1. Correctness (handles all edge cases)
            2. Simplicity and readability
            3. Adherence to Python best practices
            4. Exact match to required function signature
            5. Robustness
            
            Even though there's only one candidate, apply these criteria strictly. If it passes, return it unchanged.
            If it fails any criterion, suggest minimal improvements.""",
            contexts_list=[current_code]
        )

        # Extract just the code block from the response
        code_match = re.search(r'