# Workflow ID: mgsmbn_56_0
# Benchmark: mgsmbn
# Data Indices: [180, 53]

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

        # PHASE 1: SEMANTIC DECOMPOSITION - Extract entities, actions, constraints
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into structured components:
            1. Identify all NUMERICAL VALUES and what they represent (e.g., "15000 টাকা" = advertising budget)
            2. Identify all ENTITIES (people, objects, time periods) and their roles
            3. Identify all ACTIONS and OPERATIONS (spend, divide, compare, etc.) with their mathematical implications
            4. Identify the UNKNOWN - what is being asked ("কত?" = how much/many)
            5. Extract all CONSTRAINTS (explicit: "বাকি", "এক-তৃতীয়াংশ"; implicit: non-negative, integer-only)
            6. Note any UNIT CONVERSIONS needed (টাকা/পয়সা, ঘণ্টা/মিনিট)
            Format as clear sections with bullet points. Be exhaustive.""",
            context=""
        )

        # PHASE 2: PROBLEM CLASSIFICATION - Determine solution strategy
        classification = await self.generate(
            instruction=f"""Based on this decomposition:
            {decomposition}
            
            Classify the problem type and select appropriate solution strategy:
            - SEQUENTIAL: Multiple steps in chronological order (e.g., deposit then withdraw)
            - RATE: Involves "প্রতি" (per) - unit price, speed, work rate
            - PROPORTIONAL: Fractions, percentages, ratios ("এক-তৃতীয়াংশ", "শতকরা")
            - DISTRIBUTION: Dividing among entities, may involve remainders
            - COMPARISON: "কত বেশি/কম" (how much more/less)
            - MULTI-ENTITY: Tracking different quantities for different entities
            
            Also identify:
            - Required operations (add, subtract, multiply, divide, fractions)
            - Unit handling strategy
            - Any potential pitfalls (e.g., hidden steps, unit conversion)
            
            Output as structured JSON-like format with keys: problem_type, operations, units, pitfalls""",
            context=decomposition
        )

        # PHASE 3: PARALLEL SOLUTION ATTEMPTS - Generate multiple approaches
        # Each approach tailored to different interpretations
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""SOLUTION ATTEMPT 1: Literal interpretation
                Problem classification: {classification}
                Decomposition: {decomposition}
                
                Solve step-by-step:
                1. Write mathematical expressions for each action
                2. Show intermediate calculations
                3. Track units throughout
                4. Verify constraints (non-negative, integer if required)
                5. Box final answer
                
                Be meticulous. Show all work.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""SOLUTION ATTEMPT 2: Alternative interpretation
                Consider if problem could be solved differently:
                - Reverse order of operations?
                - Different unit interpretation?
                - Alternative mathematical model?
                
                Problem classification: {classification}
                Decomposition: {decomposition}
                
                Solve with this alternative approach. Show all steps and verify against constraints.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""SOLUTION ATTEMPT 3: Dimensional analysis approach
                Focus on units and dimensional consistency:
                - Write all quantities with units
                - Cancel units systematically
                - Verify final unit matches expected answer type
                
                Problem classification: {classification}
                Decomposition: {decomposition}
                
                Solve using unit-based reasoning. Show unit cancellation steps.""",
                context=decomposition
            )
        )

        # PHASE 4: REVISE EACH ATTEMPT - Error checking and refinement
        revised_attempts = []
        for i, attempt in enumerate(solution_attempts):
            revised = await self.revise(
                instruction=f"""CRITICALLY REVISE SOLUTION ATTEMPT {i+1}:
                - Verify every arithmetic operation (show recalculations if needed)
                - Check unit consistency throughout
                - Ensure answer respects constraints (non-negative, integer if required)
                - Flag any logical inconsistencies
                - Improve clarity of steps
                - If error found, correct it and show correction
                - Final answer must be boxed and numerical only""",
                context=attempt
            )
            revised_attempts.append(revised)

        # PHASE 5: ENSEMBLE - Synthesize best answer
        final_answer = await self.ensemble(
            instruction="""SELECT BEST ANSWER from the revised attempts:
            1. Compare numerical results - if all agree, return consensus
            2. If disagreement, evaluate which approach best respects:
               - Problem constraints
               - Unit consistency
               - Mathematical logic
               - Bengali phrasing interpretation
            3. Default to most conservative interpretation (integer, minimal assumptions)
            4. Extract ONLY the final numerical value (no units, no text)
            5. If still uncertain, choose the answer that appears in most attempts
            
            Output format: ONLY the number, nothing else.""",
            contexts_list=revised_attempts
        )

        # PHASE 6: VALIDATION - Meta-cognitive check
        validation = await self.generate(
            instruction=f"""VALIDATE FINAL ANSWER: {final_answer}
            1. Reconstruct the problem: Does this answer logically satisfy the original question?
            2. Check for reasonableness: Is the magnitude appropriate? (e.g., not negative when impossible)
            3. Verify against key constraints from decomposition
            4. If validation fails, suggest correction
            
            If validation passes, output ONLY the number. If fails, output corrected number.""",
            context=f"Original decomposition: {decomposition}\n\nFinal answer: {final_answer}"
        )

        # PHASE 7: FINAL EXTRACTION - Ensure pure numerical output
        clean_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the validation result.
            - Remove all text, units, explanations
            - If multiple numbers, select the one that answers 'কত?' (how much/many)
            - Ensure it's a valid number (integer or decimal)
            - Output ONLY the number, nothing else""",
            context=validation
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        numeric_answer = re.sub(r'[^\d.]', '', clean_answer)
        
        # Handle edge case: if empty, return original final_answer cleaned
        if not numeric_answer:
            numeric_answer = re.sub(r'[^\d.]', '', final_answer)
        
        return numeric_answer.strip()