# Workflow ID: mgsmbn_92_0
# Benchmark: mgsmbn
# Data Indices: [33, 178]

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

        # Step 1: Semantic Decomposition & Problem Classification
        initial_analysis = await self.generate(
            instruction="""Perform a deep semantic analysis of this Bengali word problem. Identify:
            1. All named entities (people, objects, places)
            2. All numerical values and their associated units (টাকা, লিটার, জিনিস, etc.)
            3. Temporal or causal sequence of events
            4. The ultimate unknown being asked for
            5. Classify the problem type: 
               - Sequential Operations (deposit/withdrawal)
               - Rate Problems (speed/time, unit price)
               - Proportional Reasoning (ratios, percentages)
               - Distribution (sharing, remainders)
               - Comparison (differences, "how many more")
               - Multi-entity Tracking
            6. List any implicit constraints (e.g., no negative quantities, whole people only)
            Format as structured markdown with clear headings.""",
            context=""
        )

        # Step 2: Generate Multiple Decompositions in Parallel
        decomposition_strategies = [
            "Focus on cost and revenue structure for profit calculation",
            "Focus on unit conversion and scaling (e.g., candles per pound)",
            "Focus on sequential state changes (initial → action → final)",
            "Focus on proportional relationships and ratios"
        ]

        decomposition_tasks = []
        for strategy in decomposition_strategies:
            task = self.decompose(
                instruction=f"""Decompose the problem using this strategy: {strategy}
                For each subproblem:
                - Clearly state what needs to be calculated
                - Specify dependencies (which previous subproblems this relies on)
                - Include units for all quantities
                - Flag any potential edge cases (division by zero, negative results)""",
                context=initial_analysis
            )
            decomposition_tasks.append(task)

        # Execute all decompositions in parallel
        all_decompositions = await asyncio.gather(*decomposition_tasks)

        # Step 3: Synthesize Best Decomposition Path
        synthesized_decomposition = await self.ensemble(
            instruction="""Evaluate all decomposition paths and select or synthesize the most coherent, complete, and logically sound approach.
            Criteria:
            1. Completeness: Does it cover all necessary steps?
            2. Correctness: Are dependencies properly ordered?
            3. Unit Consistency: Are units tracked throughout?
            4. Edge Case Handling: Are potential errors anticipated?
            5. Alignment with Problem Classification from initial analysis
            Return the selected decomposition as a numbered list of steps with dependencies.""",
            contexts_list=[str(decomp) for decomp in all_decompositions]
        )

        # Step 4: Generate Executable Code Based on Best Decomposition
        code_solution = await self.programmer(
            instruction=f"""Generate Python code that solves the problem step by step according to this decomposition:
            {synthesized_decomposition}
            
            Requirements:
            - Use descriptive variable names based on problem entities (e.g., total_candles, cost_per_pound)
            - Track units in variable names (e.g., remaining_water_liters)
            - Include comments explaining each step
            - Validate for edge cases: no negative quantities, no division by zero
            - Final answer must be stored in a variable called 'final_answer'
            - Print only the final_answer at the end (no intermediate prints)
            - If any step produces an invalid result (negative, fractional person, etc.), raise an exception with explanation""",
            context=initial_analysis
        )

        # Step 5: Validate and Revise if Necessary (up to 2 retries)
        current_solution = code_solution
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                1. Does the code logic match the problem's narrative?
                2. Are units consistent throughout?
                3. Does it handle all edge cases mentioned in initial analysis?
                4. Is the final answer format correct (single number, appropriate precision)?
                5. Would this solution make sense to a 5th grader?
                If any issues are found, describe them specifically. Otherwise, say 'VALID'.""",
                context=current_solution
            )
            
            if "VALID" in validation.upper():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix these issues:
                    {validation}
                    
                    Requirements:
                    - Maintain the step-by-step structure
                    - Preserve unit tracking
                    - Ensure final answer is still stored in 'final_answer'
                    - Add comments explaining the fixes""",
                    context=current_solution
                )
        else:
            # If all retries fail, fall back to initial decomposition
            current_solution = code_solution

        # Step 6: Extract and Normalize Final Numerical Answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.
            Rules:
            - Remove any units, labels, or explanatory text
            - If the answer is a whole number (e.g., 20.0), output as integer (20)
            - If decimal is necessary (e.g., 15.5), keep as float
            - Ensure no extra spaces or formatting
            - If multiple numbers appear, select the one that matches the problem's ultimate question
            Output ONLY the number, nothing else.""",
            context=current_solution
        )

        # Clean the final answer (remove any non-numeric characters except decimal point)
        cleaned_answer = re.sub(r'[^\d\.]', '', final_answer.strip())
        
        # Convert to int if it's a whole number, otherwise float
        if '.' in cleaned_answer:
            final_numeric = float(cleaned_answer)
            if final_numeric.is_integer():
                final_numeric = int(final_numeric)
        else:
            final_numeric = int(cleaned_answer) if cleaned_answer else 0

        return str(final_numeric)