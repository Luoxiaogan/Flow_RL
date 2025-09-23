# Workflow ID: mbppplus_157_0
# Benchmark: mbppplus
# Data Indices: [278, 231]

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

        # Step 1: Classify the problem type and extract key requirements
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it:
            1. Identify the input type (string, list, number, etc.) and output type.
            2. Determine the core operation: is it pattern matching, data extraction, mathematical computation, set operation, or logical validation?
            3. Note any explicit or implicit constraints (e.g., handle edge cases, preserve order, specific return type).
            4. Infer expected edge cases (empty inputs, single elements, duplicates, boundary values).
            5. Suggest 2-3 potential solution strategies (e.g., regex, iteration, built-in functions).
            Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Conditionally decompose if problem is multi-step
        decomposition_needed = await self.generate(
            instruction=f"""Based on this classification:
            {classification}
            
            Determine if this problem requires decomposition into subproblems. 
            Answer only 'YES' if it involves multiple distinct steps or phases, otherwise 'NO'.""",
            context=classification
        )

        subproblems = []
        if "YES" in decomposition_needed.upper():
            subproblems_raw = await self.decompose(
                instruction="""Break this problem into minimal, independent subproblems.
                Each subproblem should be solvable in isolation and contribute directly to the final solution.
                Return a list of subproblem dictionaries with 'id', 'description', and 'dependencies'.""",
                context=classification
            )
            subproblems = subproblems_raw

        # Step 3: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Devise a solution strategy focusing on string methods and regular expressions.
            Detail step-by-step how to process the input, handle edge cases, and produce the output.
            Include specific regex patterns or string operations if applicable.""",
            
            """Devise a solution strategy focusing on iterative parsing and manual data extraction.
            Detail how to traverse the input, identify key elements, transform data, and construct the output.
            Emphasize explicit loops and conditionals for robustness.""",
            
            """Devise a solution strategy leveraging Python's built-in functions and libraries.
            Detail which modules (re, itertools, collections, etc.) to import and how to use them efficiently.
            Focus on concise, idiomatic Python code."""
        ]

        strategy_context = classification
        if subproblems:
            strategy_context += f"\n\nSubproblems to consider: {subproblems}"

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context=strategy_context) for instr in strategy_instructions]
        )

        # Step 4: Convert strategies to code candidates
        code_candidates = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Generate a complete Python function based on this strategy:
                {strategy}
                
                Requirements:
                - Use EXACT function name and signature from the problem.
                - Include necessary imports inside the function if needed.
                - Handle all edge cases mentioned in the strategy.
                - Return the correct data type.
                - Output ONLY the function code in a markdown code block.""",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 5: Validate and revise each code candidate
        validated_candidates = []
        for candidate in code_candidates:
            validation = await self.generate(
                instruction=f"""Critically evaluate this code solution:
                {candidate}
                
                Check for:
                1. Correct function signature and name.
                2. Proper handling of edge cases (empty input, single elements, boundaries).
                3. Correct return type and data structure.
                4. Potential bugs or logical errors.
                5. Efficiency and readability.
                
                If issues are found, suggest specific revisions. Otherwise, say 'VALID'.""",
                context=candidate
            )
            
            if "VALID" not in validation.upper():
                revised = await self.revise(
                    instruction=f"""Fix all issues identified in the validation:
                    {validation}
                    
                    Maintain the original function signature and core logic.
                    Ensure edge cases are handled.
                    Output ONLY the corrected function code in a markdown code block.""",
                    context=candidate
                )
                validated_candidates.append(revised)
            else:
                validated_candidates.append(candidate)

        # Step 6: Ensemble select the best solution
        final_code = await self.ensemble(
            instruction="""Select the best solution from these candidates:
            Criteria:
            1. Correctness: handles all edge cases and matches problem requirements.
            2. Robustness: least likely to fail on unseen test cases.
            3. Readability: clear, well-structured code.
            4. Efficiency: optimal time/space complexity.
            
            Extract ONLY the function code block from the chosen solution.
            Ensure it includes necessary imports and matches the required signature exactly.""",
            contexts_list=validated_candidates
        )

        # Step 7: Extract clean code (remove markdown if present)
        if "