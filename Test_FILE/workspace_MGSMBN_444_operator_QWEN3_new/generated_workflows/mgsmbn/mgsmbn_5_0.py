# Workflow ID: mgsmbn_5_0
# Benchmark: mgsmbn
# Data Indices: [0, 71]

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

        # STEP 1: PARALLEL PROBLEM DECOMPOSITION (Diamond Fork)
        decomposition_tasks = [
            self.generate(
                instruction="""Perform a mathematical decomposition of the Bengali word problem:
                - Identify all numerical values and their associated units (টাকা, ডলার, বছর, টি, etc.)
                - Map relationships between entities (who has what, who is older, what depends on what)
                - Translate comparative statements into mathematical operations (+, -, ×, ÷, =)
                - Flag any ambiguous or missing information
                Output in structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Perform a logical decomposition of the Bengali word problem:
                - Identify all entities (people, objects, time periods)
                - Extract all comparative or relational statements (older than, more than, after, before)
                - Represent relationships as logical dependencies or equations
                - Identify the unknown variable to solve for
                Output in structured bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Perform a contextual/real-world decomposition of the Bengali word problem:
                - Identify real-world constraints (no negative ages, whole people, positive money)
                - Infer implicit assumptions (e.g., daily routines, market prices)
                - Identify potential edge cases or trick elements
                - Suggest plausible solution strategies based on context
                Output in structured bullet points.""",
                context=""
            )
        ]
        
        decompositions = await asyncio.gather(*decomposition_tasks)
        
        # STEP 2: SYNTHESIZE DECOMPOSITIONS & CLASSIFY PROBLEM TYPE
        synthesis = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives (mathematical, logical, contextual) into a unified problem understanding.
            Then classify the problem into one primary type:
            - "SEQUENTIAL_ARITHMETIC": Multi-step calculations with clear order (e.g., deposit then withdraw)
            - "AGE_CHAIN_DEDUCTION": Age comparisons forming a solvable equation chain
            - "RATE_OPTIMIZATION": Involves rates, prices, or unit conversions
            - "DISTRIBUTION_SHARING": Dividing quantities with remainders or equal shares
            - "COMPARISON_DIFFERENCE": Finding "how many more" or differences
            - "MULTI_ENTITY_TRACKING": Multiple entities with interdependent quantities
            
            Output format:
            SYNTHESIS: [concise unified summary]
            CLASSIFICATION: [one of the above types]""",
            contexts_list=decompositions
        )
        
        # Extract classification for branching
        problem_type = ""
        if "SEQUENTIAL_ARITHMETIC" in synthesis:
            problem_type = "SEQUENTIAL_ARITHMETIC"
        elif "AGE_CHAIN_DEDUCTION" in synthesis:
            problem_type = "AGE_CHAIN_DEDUCTION"
        elif "RATE_OPTIMIZATION" in synthesis:
            problem_type = "RATE_OPTIMIZATION"
        elif "DISTRIBUTION_SHARING" in synthesis:
            problem_type = "DISTRIBUTION_SHARING"
        elif "COMPARISON_DIFFERENCE" in synthesis:
            problem_type = "COMPARISON_DIFFERENCE"
        elif "MULTI_ENTITY_TRACKING" in synthesis:
            problem_type = "MULTI_ENTITY_TRACKING"
        else:
            problem_type = "GENERAL_ARITHMETIC"  # Fallback

        # STEP 3: CONDITIONAL STRATEGY EXECUTION
        strategy_instruction = ""
        
        if problem_type == "AGE_CHAIN_DEDUCTION":
            strategy_instruction = """Solve this age comparison problem using algebraic deduction:
            - Assign variables to unknown ages (e.g., let Jackson's age = J)
            - Translate each comparative statement into an equation (e.g., "Amy is 5 years older than Jackson" → A = J + 5)
            - Build a system of equations
            - Solve step by step through substitution
            - Verify all ages are positive integers
            - State the final answer clearly."""
            
        elif problem_type == "RATE_OPTIMIZATION":
            strategy_instruction = """Solve this rate/price problem with unit tracking:
            - Identify base quantities and rates (e.g., eggs per day, price per egg)
            - Calculate intermediate quantities (e.g., eggs used, eggs remaining)
            - Apply rates to compute final value (e.g., revenue = remaining eggs × price per egg)
            - Track units throughout (ensure dollars, eggs, days are consistent)
            - State the final answer clearly."""
            
        elif problem_type == "SEQUENTIAL_ARITHMETIC":
            strategy_instruction = """Solve this multi-step arithmetic problem chronologically:
            - Break into ordered steps (Step 1, Step 2, ...)
            - Perform each calculation sequentially
            - Carry forward results to next step
            - Verify intermediate values make real-world sense (no negatives, fractions where inappropriate)
            - State the final answer clearly."""
            
        elif problem_type == "DISTRIBUTION_SHARING":
            strategy_instruction = """Solve this distribution problem with remainder awareness:
            - Identify total quantity and number of recipients
            - Perform division to find shares
            - Calculate and interpret remainders
            - Apply real-world constraints (e.g., can't split people)
            - State the final answer clearly."""
            
        elif problem_type == "COMPARISON_DIFFERENCE":
            strategy_instruction = """Solve this comparison problem by finding differences:
            - Identify the two quantities being compared
            - Subtract smaller from larger (or as specified)
            - Interpret "how many more" or "how much less" correctly
            - State the final answer clearly."""
            
        elif problem_type == "MULTI_ENTITY_TRACKING":
            strategy_instruction = """Solve this multi-entity problem by tracking each entity:
            - Create a table or list for each entity's quantity
            - Update quantities based on relationships
            - Ensure conservation of total where applicable
            - State the final answer clearly."""
            
        else:  # GENERAL_ARITHMETIC
            strategy_instruction = """Solve this general arithmetic problem:
            - Identify known values and unknown
            - Determine required operations
            - Perform calculations step by step
            - Verify result makes contextual sense
            - State the final answer clearly."""

        # Generate initial solution
        solution_draft = await self.generate(
            instruction=f"""{strategy_instruction}

            Use the following problem understanding to guide your solution:
            {synthesis}

            Show all steps clearly. Box your final numerical answer at the end.""",
            context=synthesis
        )

        # STEP 4: VALIDATE AND REVISE (Cascade with Feedback)
        validation = await self.generate(
            instruction="""Critically validate the solution draft:
            - Check arithmetic for calculation errors
            - Verify units are consistent and correctly applied
            - Ensure answer matches the question asked
            - Confirm real-world plausibility (no negative ages, fractional people, etc.)
            - If any issues found, describe them specifically.
            If no issues, output "VALID". Otherwise, list all errors.""",
            context=solution_draft
        )

        final_solution = solution_draft
        if "VALID" not in validation.upper():
            final_solution = await self.revise(
                instruction=f"""Revise the solution to fix the following issues:
                {validation}

                Maintain all correct parts. Only modify what's necessary.
                Ensure final answer is still boxed at the end.""",
                context=solution_draft
            )

        # STEP 5: EXTRACT FINAL NUMERICAL ANSWER
        answer = await self.revise(
            instruction="""Extract ONLY the final numerical answer from the solution.
            - It should be a single integer or decimal number
            - Remove all units, labels, and explanations
            - If multiple numbers, select the one that answers the original question
            - If uncertain, choose the last computed numerical value
            Output ONLY the number, nothing else.""",
            context=final_solution
        )

        # Clean answer (remove any non-numeric characters except decimal point)
        cleaned_answer = re.sub(r'[^\d.]', '', answer.strip())
        
        return cleaned_answer