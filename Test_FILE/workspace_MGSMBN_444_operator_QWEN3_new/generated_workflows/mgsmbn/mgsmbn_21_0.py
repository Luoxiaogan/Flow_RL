# Workflow ID: mgsmbn_21_0
# Benchmark: mgsmbn
# Data Indices: [139, 20]

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

        # STEP 1: STRUCTURAL EXTRACTION
        extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract all mathematical components in a structured format. Identify:
            - ENTITIES: All objects, people, or items mentioned with their quantities (e.g., '80টি মাকড়সা', '90টি পতঙ্গ')
            - ATTRIBUTES: Properties associated with entities (e.g., '8টি পা', 'প্রতি কার্টন $4.00')
            - ACTIONS: Operations or changes described (e.g., 'দেখেন', 'ক্রয় করেন', 'খান')
            - RELATIONSHIPS: How entities interact mathematically (e.g., multiplication, division, addition)
            - CONSTRAINTS: Real-world limitations (e.g., 'can't have negative items', 'must buy whole cartons')
            - GOAL: What the problem is asking to find (e.g., 'মোট কতগুলি পা', 'ব্যয় করা অর্থের পরিমাণ')
            
            Format your output as clearly labeled sections. Be exhaustive and precise.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION STRATEGIES
        strategy_instructions = [
            """Solve using direct arithmetic computation. Break down into sequential steps. Show all intermediate calculations. Track units at every step. Convert units when necessary. Round final answer appropriately. Verify that each step logically follows from the problem description.""",
            """Solve using algebraic modeling. Define variables for unknowns. Set up equations based on relationships. Solve step by step. Show substitution and simplification. Verify solution against original problem constraints.""",
            """Solve using proportional reasoning. Identify ratios, rates, or scaling factors. Set up proportions. Cross-multiply and solve. Check that proportions match problem context. Handle unit conversions explicitly."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=extraction) for instr in strategy_instructions]
        )

        # STEP 3: ADVERSARIAL CRITIQUE
        critiques = await asyncio.gather(
            *[self.generate(
                instruction=f"""Critically evaluate the following solution attempt for mathematical and logical correctness:
                - Check arithmetic accuracy
                - Verify unit consistency and conversions
                - Ensure order of operations is correct
                - Confirm real-world constraints are respected (no negative quantities, whole items when required)
                - Validate that the solution addresses the problem's goal
                - Flag any ambiguous or unsupported assumptions
                
                If errors are found, describe them specifically. If no errors, state "VALID".
                """,
                context=attempt
            ) for attempt in solution_attempts]
        )

        # STEP 4: SYNTHESIZE WITH ERROR CORRECTION
        synthesis_contexts = [
            f"Solution Attempt:\n{sol}\n\nCritique:\n{crit}" 
            for sol, crit in zip(solution_attempts, critiques)
        ]
        
        synthesized = await self.ensemble(
            instruction="""You are given multiple solution attempts with their critiques. Your task:
            1. Identify the most mathematically sound solution
            2. If a solution has correct logic but arithmetic errors, fix the arithmetic
            3. If multiple solutions are partially correct, synthesize the best elements
            4. If all solutions have fundamental flaws, create a new correct solution
            5. Present the final solution as a clear, step-by-step calculation with explanations
            6. State the final numerical answer prominently at the end""",
            contexts_list=synthesis_contexts
        )

        # STEP 5: VALIDITY CHECK & UNCERTAINTY DETECTION
        validity_check = await self.summarize(
            instruction="""Summarize the final solution into one sentence stating the answer and key steps. 
            If any step is ambiguous, mathematically unsupported, or based on assumptions not in the problem, 
            append 'UNCERTAIN: [reason]'. Otherwise, append 'CONFIDENT'.""",
            context=synthesized
        )

        # STEP 6: CONDITIONAL RE-ANALYSIS IF UNCERTAIN
        if "UNCERTAIN" in validity_check:
            refined_extraction = await self.revise(
                instruction=f"""Re-analyze the original problem with extreme care. Previous analysis was flagged as uncertain because: {validity_check}
                Focus on:
                - Re-examining all quantities and their relationships
                - Clarifying ambiguous phrases
                - Verifying unit interpretations
                - Ensuring no entities or actions were missed
                Output a more precise, unambiguous structural breakdown.""",
                context=extraction
            )
            
            # Quick re-solve with refined extraction
            fallback_solution = await self.generate(
                instruction="""Using the refined problem analysis, solve directly with arithmetic. 
                Show only essential steps. Be meticulous about units and conversions. 
                State final answer clearly.""",
                context=refined_extraction
            )
            final_output = fallback_solution
        else:
            final_output = synthesized

        # STEP 7: FINAL ANSWER EXTRACTION
        answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution below. 
            Rules:
            - No units, explanations, or punctuation
            - If decimal, round to 2 places unless problem specifies otherwise
            - If multiple numbers appear, select the one that answers the problem's explicit question
            - If no clear answer, return '0'
            
            Return ONLY the number.""",
            context=final_output
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', answer.strip())
        
        # Handle edge case where multiple decimals might appear
        if cleaned_answer.count('.') > 1:
            parts = cleaned_answer.split('.')
            cleaned_answer = parts[0] + '.' + ''.join(parts[1:])
            
        return cleaned_answer