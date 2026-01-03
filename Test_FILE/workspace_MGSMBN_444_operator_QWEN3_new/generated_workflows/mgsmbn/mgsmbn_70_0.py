# Workflow ID: mgsmbn_70_0
# Benchmark: mgsmbn
# Data Indices: [101, 12]

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

        # PHASE 1: PARALLEL PROBLEM DECONSTRUCTION
        # Extract entities, actions, and relationships from multiple perspectives
        entity_extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract all mathematical entities and relationships. 
            Identify:
            - All numerical values and what they represent (e.g., "5টি প্যাকেট" → 5 packets)
            - All actors/objects (e.g., Julia, spoons, trains)
            - All actions with temporal or causal relationships (e.g., "কিনে এনেছিলেন" → purchased, "ব্যবহার করেছিলেন" → used)
            - The unknown being asked for (e.g., "কতগুলি চামচ" → how many spoons)
            - Units of measurement (টাকা, মাইল, জিনিস, etc.)
            - Any implicit constraints (e.g., non-negative quantities, whole numbers for countable items)
            
            Structure your output as:
            ENTITIES: [list with descriptions]
            ACTIONS: [chronological list with dependencies]
            UNKNOWN: [clearly state what needs to be solved for]
            CONSTRAINTS: [list any real-world or mathematical constraints]
            """,
            context=""
        )

        # PHASE 2: PROBLEM CLASSIFICATION
        problem_type = await self.generate(
            instruction=f"""Based on the extracted structure:
            {entity_extraction}
            
            Classify this problem into one or more of the following categories:
            - Sequential Operations (multiple steps in order)
            - Algebraic Unknown (requires setting up and solving an equation)
            - Proportional Reasoning (ratios, percentages, scaling)
            - Distribution/Division (sharing, remainders)
            - Comparison (differences, "how many more")
            - Multi-entity Tracking (multiple objects/people with different quantities)
            - Distance/Rate/Time (speed, travel, time calculations)
            
            Also determine:
            - Is the solution path forward-calculation or reverse-engineering?
            - Are units consistent or do they need conversion?
            - Is the answer expected to be integer, decimal, or fraction?
            
            Output your classification in a structured format.""",
            context=entity_extraction
        )

        # PHASE 3: PARALLEL STRATEGY GENERATION
        # Generate multiple solution approaches based on classification
        async def generate_strategy(strategy_type, context):
            return await self.generate(
                instruction=f"""You are solving a math word problem classified as: {strategy_type}
                
                Problem context:
                {context}
                
                Strategy: {strategy_type.upper()} APPROACH
                - If ALGEBRAIC: Define variables for unknowns, write equations, solve step-by-step, verify solution.
                - If SEQUENTIAL: Simulate each step chronologically, track state changes, compute final value.
                - If PROPORTIONAL: Set up ratios or percentages, cross-multiply or scale, solve for unknown.
                - If COMPARISON: Calculate differences, identify what is being compared, compute gap.
                - If MULTI-ENTITY: Track each entity separately, then combine or compare as needed.
                
                Show all intermediate steps clearly.
                Verify that your final answer satisfies all constraints from the problem.
                Your final output must end with: "ANSWER: [numerical value]" (no units, no explanation).""",
                context=context
            )

        # Extract strategy keywords for parallel execution
        strategies = []
        if "Algebraic" in problem_type or "Unknown" in problem_type:
            strategies.append("algebraic")
        if "Sequential" in problem_type or "Step" in problem_type:
            strategies.append("sequential")
        if "Proportional" in problem_type or "Ratio" in problem_type or "Percentage" in problem_type:
            strategies.append("proportional")
        if "Comparison" in problem_type:
            strategies.append("comparison")
        if "Multi-entity" in problem_type:
            strategies.append("multi-entity")
        
        # Default: if no clear strategy, try sequential and algebraic
        if len(strategies) == 0:
            strategies = ["sequential", "algebraic"]

        # Generate solutions in parallel
        solution_tasks = [generate_strategy(strategy, entity_extraction) for strategy in strategies]
        raw_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 4: VALIDATION & REVISION
        async def validate_solution(solution):
            return await self.revise(
                instruction="""Critically evaluate this solution:
                - Check all arithmetic calculations for accuracy.
                - Verify unit consistency (convert if needed).
                - Ensure the answer satisfies real-world constraints (e.g., no negative spoons, whole numbers for countable items).
                - Confirm the solution addresses the original question.
                - If any error is found, correct it and explain the fix.
                - If the approach is fundamentally flawed, state why and mark as INVALID.
                
                Your output must end with "ANSWER: [numerical value]" if valid, or "INVALID" if not.""",
                context=solution
            )

        validation_tasks = [validate_solution(sol) for sol in raw_solutions]
        validated_solutions = await asyncio.gather(*validation_tasks)

        # Filter out invalid solutions
        valid_solutions = []
        for sol in validated_solutions:
            if "INVALID" not in sol and "ANSWER:" in sol:
                # Extract just the numerical answer
                match = re.search(r'ANSWER:\s*([0-9]+\.?[0-9]*)', sol)
                if match:
                    valid_solutions.append(match.group(1))

        # If no valid solutions, fall back to original raw solutions (emergency mode)
        if len(valid_solutions) == 0:
            for sol in raw_solutions:
                match = re.search(r'ANSWER:\s*([0-9]+\.?[0-9]*)', sol)
                if match:
                    valid_solutions.append(match.group(1))
            # If still nothing, use first raw solution as is
            if len(valid_solutions) == 0 and len(raw_solutions) > 0:
                valid_solutions = [raw_solutions[0]]

        # PHASE 5: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""You are given multiple candidate numerical answers for the same math problem.
            Your task:
            - If all answers agree, output that number.
            - If answers conflict, analyze which solution path is most mathematically sound and contextually appropriate.
            - Consider which approach best handles the problem's constraints and hidden complexities.
            - Choose the single best answer.
            
            CRITICAL: Your output must be ONLY the numerical value, with no units, no explanation, no punctuation.
            Example outputs: "10", "230", "15.5" — nothing else.""",
            contexts_list=valid_solutions if len(valid_solutions) > 0 else ["0"]  # Fallback to 0 if all else fails
        )

        # Clean final answer (extract just the number)
        match = re.search(r'([0-9]+\.?[0-9]*)', final_answer)
        if match:
            return match.group(1)
        else:
            # Ultimate fallback
            return "0"