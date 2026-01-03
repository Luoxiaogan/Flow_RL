# Workflow ID: mgsmbn_57_0
# Benchmark: mgsmbn
# Data Indices: [59, 105]

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
        decomposition = await self.decompose(
            instruction="""Break this Bengali math word problem into atomic, solvable subproblems.
            Each subproblem must:
            - Be self-contained with clear inputs and expected output
            - Specify required operations (add, multiply, compare, etc.)
            - Include relevant extracted numbers and units from the problem
            - Define dependencies ONLY if output of one subproblem is input to another
            - Use simple, imperative language (e.g., "Calculate total cost if buying 6 packages at $2.50 each")
            - Assume no prior knowledge beyond what's stated
            Return as list of dictionaries with 'id', 'description', 'dependencies'""",
            context=""
        )

        # STEP 2: VALIDATE DECOMPOSITION
        decomposition_text = "\n".join([f"{d['id']}: {d['description']} (Depends on: {d['dependencies']})" for d in decomposition])
        validation = await self.revise(
            instruction=f"""Critically review this decomposition against the original problem:
            Original Problem: {self.problem_text}
            Proposed Decomposition:
            {decomposition_text}

            Check for:
            1. Missing subproblems (e.g., unit conversions, intermediate comparisons)
            2. Incorrect dependencies (e.g., circular or missing prerequisites)
            3. Misinterpreted quantities or relationships
            4. Violations of real-world constraints (negative people, fractional items when inappropriate)
            5. Ambiguous descriptions that lack specific numbers or operations

            If any issues found, rewrite the ENTIRE decomposition list with fixes. Otherwise, return 'VALIDATED'.""",
            context=decomposition_text
        )

        if "VALIDATED" not in validation:
            # Regenerate decomposition if invalid
            decomposition = await self.decompose(
                instruction=f"""Previous decomposition had errors. Regenerate with corrections:
                Feedback: {validation}
                
                Break this Bengali math word problem into atomic, solvable subproblems.
                Each subproblem must:
                - Be self-contained with clear inputs and expected output
                - Specify required operations (add, multiply, compare, etc.)
                - Include relevant extracted numbers and units from the problem
                - Define dependencies ONLY if output of one subproblem is input to another
                - Use simple, imperative language (e.g., "Calculate total cost if buying 6 packages at $2.50 each")
                - Assume no prior knowledge beyond what's stated
                Return as list of dictionaries with 'id', 'description', 'dependencies'""",
                context=""
            )

        # STEP 3: PARALLEL SUBPROBLEM SOLVING
        async def solve_subproblem(subproblem):
            # Generate precise programmer instruction
            prog_instruction = f"""Solve this math subproblem with Python code:
            Problem: {subproblem['description']}
            Requirements:
            - Use ONLY the numbers and relationships explicitly stated
            - Track units throughout (টাকা, জন, টি, etc.) but return only the numerical answer
            - If division results in decimal, round appropriately based on context (people→integer, money→2 decimals)
            - Validate result makes sense (no negative counts, etc.)
            - Return ONLY the final number, nothing else
            - If error, return 'ERROR'"""

            result = await self.programmer(
                instruction=prog_instruction,
                context="",
                max_retries=2
            )
            
            # Extract number from result
            match = re.search(r'([-+]?\d*\.?\d+)', result)
            if match:
                return float(match.group(1)) if '.' in match.group(1) else int(float(match.group(1)))
            else:
                # Fallback: generate natural language solution
                fallback = await self.generate(
                    instruction=f"""Solve step-by-step without code:
                    {subproblem['description']}
                    Return ONLY the final number.""",
                    context=""
                )
                match = re.search(r'([-+]?\d*\.?\d+)', fallback)
                if match:
                    return float(match.group(1)) if '.' in match.group(1) else int(float(match.group(1)))
                return 0  # Default fallback

        # Solve all subproblems in parallel
        subproblem_tasks = [solve_subproblem(sp) for sp in decomposition]
        subproblem_results = await asyncio.gather(*subproblem_tasks)
        
        # Create results mapping
        results_map = {decomposition[i]['id']: subproblem_results[i] for i in range(len(decomposition))}

        # STEP 4: SYNTHESIZE FINAL ANSWER
        synthesis_context = "\n".join([f"{decomposition[i]['id']}: {subproblem_results[i]} (from: {decomposition[i]['description']})" for i in range(len(decomposition))])
        
        final_answer = await self.generate(
            instruction=f"""Synthesize final answer from these subproblem results:
            {synthesis_context}
            
            Steps:
            1. Identify which subproblem result directly answers the original question
            2. If multiple candidates, select the one that matches the question's final requirement
            3. Apply any final operations (e.g., difference between two subproblem results)
            4. Ensure unit and format match problem's expectation (integer for counts, decimal for money)
            5. Return ONLY the final number, nothing else""",
            context=synthesis_context
        )

        # STEP 5: ENSEMBLE VERIFICATION (Generate alternative solution paths)
        alternative_approaches = await asyncio.gather(
            self.generate(
                instruction="""Solve the original problem using a completely different method:
                - If original used packages, use unit pricing
                - If original used subtraction, use addition of remainders
                - Show all steps but return ONLY final number""",
                context=""
            ),
            self.generate(
                instruction="""Solve by dimensional analysis or proportion:
                - Set up ratios or proportions
                - Cross-multiply and solve
                - Return ONLY final number""",
                context=""
            )
        )

        # Extract numbers from alternatives
        alt_numbers = []
        for alt in alternative_approaches:
            match = re.search(r'([-+]?\d*\.?\d+)', alt)
            if match:
                num = float(match.group(1)) if '.' in match.group(1) else int(float(match.group(1)))
                alt_numbers.append(str(num))

        # Add our computed answer to alternatives
        match = re.search(r'([-+]?\d*\.?\d+)', final_answer)
        if match:
            computed_answer = float(match.group(1)) if '.' in match.group(1) else int(float(match.group(1)))
            alt_numbers.append(str(computed_answer))
        else:
            computed_answer = 0

        # Ensemble vote
        if len(alt_numbers) > 1:
            ensemble_result = await self.ensemble(
                instruction="""Select the most consistent and mathematically sound answer:
                - Prefer answers that appear multiple times
                - Validate against original problem constraints
                - Eliminate answers violating real-world logic (negative, fractional people)
                - Return ONLY the selected number""",
                contexts_list=alt_numbers
            )
            match = re.search(r'([-+]?\d*\.?\d+)', ensemble_result)
            if match:
                return match.group(1)

        # Fallback to computed answer
        return str(computed_answer)