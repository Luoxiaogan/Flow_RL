# Workflow ID: mgsmbn_15_0
# Benchmark: mgsmbn
# Data Indices: [7]

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

        # STEP 1: SEMANTIC DECOMPOSITION
        # Break problem into atomic, solvable subproblems with clear dependencies
        decomposition_instruction = """
        Systematically decompose this Bengali word problem into minimal, independent mathematical subproblems.
        For each subproblem:
        - Identify the exact quantities, units, and operations involved
        - Specify what needs to be calculated (e.g., "cost of 3 dozen donuts at $68/dozen")
        - Note any dependencies (e.g., "requires result from subproblem 2")
        - Treat every distinct purchase, distance, time, or distribution as separate
        - Include hidden steps (e.g., unit conversions, intermediate totals)
        - Format each subproblem as a clear, imperative calculation task
        Focus on mathematical relationships, not narrative structure.
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # If decomposition fails or returns empty, fall back to direct solve
        if not subproblems or len(subproblems) == 0:
            direct_solve = await self.generate(
                instruction="Solve this Bengali math problem directly. Show all steps clearly and output only the final numerical answer.",
                context=""
            )
            # Extract number from response
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', direct_solve)
            return float(numbers[0]) if numbers else 0

        # STEP 2: PARALLEL NATURAL LANGUAGE MODELING
        # Convert each subproblem into a natural language calculation description
        async def model_subproblem(subproblem):
            modeling_instruction = f"""
            Given this mathematical subproblem from a Bengali word problem:
            "{subproblem['description']}"
            
            Write a clear, step-by-step natural language explanation of the exact arithmetic operation needed.
            Include:
            - The numbers and units involved
            - The operation (multiply, divide, add, subtract, etc.)
            - Why this operation is appropriate
            - Any unit conversions required
            - The expected output format
            
            Example: "Multiply 3 (dozens) by 68 (dollars per dozen) to get the total cost of donuts in dollars."
            """
            return await self.generate(
                instruction=modeling_instruction,
                context=""
            )

        # Generate all subproblem models in parallel
        subproblem_models = await asyncio.gather(
            *[model_subproblem(sp) for sp in subproblems]
        )

        # STEP 3: PARALLEL CODE GENERATION & EXECUTION
        # Convert each natural language model into executable code and run it
        async def execute_subproblem(model, idx):
            for attempt in range(3):  # Max 3 retries
                try:
                    code_instruction = f"""
                    Convert this natural language calculation into executable Python code:
                    "{model}"
                    
                    Requirements:
                    - Output ONLY the numerical result (no text, no print statements)
                    - Use float or int as appropriate
                    - Handle unit conversions if mentioned
                    - Assume all inputs are provided in the description
                    - If division, use float division
                    - No external libraries
                    """
                    
                    result = await self.programmer(
                        instruction=code_instruction,
                        context=model,
                        max_retries=1
                    )
                    
                    # Extract numerical result from code output
                    numbers = re.findall(r'[-+]?\d*\.\d+|\d+', result)
                    if numbers:
                        return float(numbers[0])
                    else:
                        raise ValueError("No number found in result")
                        
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise e
                    # Revise the model and retry
                    revised_model = await self.revise(
                        instruction=f"""
                        The following calculation model failed to produce a valid numerical result:
                        "{model}"
                        
                        Error: {str(e)}
                        
                        Revise this model to be more precise:
                        - Clarify any ambiguous operations
                        - Specify units explicitly
                        - Break down complex operations into simpler steps
                        - Ensure the description leads to a single numerical output
                        """,
                        context=model
                    )
                    model = revised_model

        # Execute all subproblems in parallel
        subproblem_results = await asyncio.gather(
            *[execute_subproblem(model, i) for i, model in enumerate(subproblem_models)],
            return_exceptions=True
        )

        # Handle any failures
        for i, result in enumerate(subproblem_results):
            if isinstance(result, Exception):
                # Fallback: try direct calculation for this subproblem
                fallback_instruction = f"""
                Directly calculate this subproblem from the original Bengali text:
                "{subproblems[i]['description']}"
                
                Output only the numerical result.
                """
                fallback_result = await self.generate(
                    instruction=fallback_instruction,
                    context=""
                )
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', fallback_result)
                subproblem_results[i] = float(numbers[0]) if numbers else 0

        # STEP 4: SYNTHESIZE FINAL ANSWER
        # Generate multiple strategies for combining sub-results
        synthesis_strategies = [
            """
            Strategy A: Simple Summation
            Add all subproblem results together. This is appropriate when the problem asks for a total, sum, or combined amount.
            Formula: result = sum(all_subproblem_results)
            """,
            """
            Strategy B: Weighted or Conditional Combination
            Apply weights, ratios, or conditions based on the problem context. For example, if some results are per-unit and others are totals, convert to common units first.
            """,
            """
            Strategy C: Difference or Comparison
            If the problem asks for difference, remaining, or comparison, subtract appropriate values.
            Formula: result = max(subproblem_results) - min(subproblem_results)  (or other specified comparison)
            """
        ]

        # Generate synthesis code for each strategy
        async def generate_synthesis_code(strategy, results):
            code_instruction = f"""
            Given these subproblem results: {results}
            
            Implement this synthesis strategy:
            "{strategy}"
            
            Write Python code that outputs only the final numerical answer.
            Consider:
            - Units consistency
            - Problem context (total, difference, ratio, etc.)
            - Any explicit instructions in the original problem
            """
            try:
                result = await self.programmer(
                    instruction=code_instruction,
                    context="",
                    max_retries=2
                )
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', result)
                return float(numbers[0]) if numbers else None
            except:
                return None

        # Generate all synthesis attempts in parallel
        synthesis_results = await asyncio.gather(
            *[generate_synthesis_code(strategy, subproblem_results) for strategy in synthesis_strategies]
        )

        # Filter out None results
        valid_synthesis_results = [r for r in synthesis_results if r is not None]

        if not valid_synthesis_results:
            # Final fallback: sum all results
            final_answer = sum(subproblem_results)
        else:
            # Use Ensemble to select best synthesis
            synthesis_selection = await self.ensemble(
                instruction="""
                You are given multiple numerical results from different synthesis strategies.
                Select the result that:
                1. Matches the problem's requested output (total, difference, etc.)
                2. Is mathematically consistent with the subproblem results
                3. Has no unit mismatches
                4. Is most likely correct based on the original problem context
                
                If multiple are valid, choose the one from Strategy A (Simple Summation) unless the problem clearly requires otherwise.
                Output only the selected numerical value.
                """,
                contexts_list=[str(r) for r in valid_synthesis_results]
            )
            
            # Extract number from ensemble result
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', synthesis_selection)
            final_answer = float(numbers[0]) if numbers else sum(subproblem_results)

        return final_answer