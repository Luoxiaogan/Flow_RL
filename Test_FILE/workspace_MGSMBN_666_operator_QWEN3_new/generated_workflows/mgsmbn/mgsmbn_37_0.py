# Workflow ID: mgsmbn_37_0
# Benchmark: mgsmbn
# Data Indices: [139, 194]

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

        # === PHASE 1: SEMANTIC GROUNDING ===
        # Extract entities, quantities, relationships, and target question
        grounding_instruction = """
        Analyze the Bengali word problem with extreme precision. Your task is to extract and categorize:

        1. ENTITIES: All named objects, people, creatures, or groups (e.g., "মাকড়সা", "মাইক", "পতঙ্গ")
        2. QUANTITIES: All numerical values with their associated entities and units (e.g., "80টি মাকড়সা", "প্রতি সপ্তাহে 2টি চিঠি")
        3. RELATIONSHIPS: How entities interact (e.g., "প্রত্যেকে প্রতি সপ্তাহে 2টি চিঠি পাঠায়", "10টি পা বিশিষ্ট")
        4. TARGET: Exactly what is being asked (e.g., "মোট কতগুলি পা", "কত ঘণ্টা ব্যয় করে")
        5. CONSTRAINTS: Any implicit or explicit limitations (e.g., "প্রতি 6 মিনিটে এক পৃষ্ঠা", "ত্যাগ করেছিল")

        Format your output as a structured JSON-like block with clear section headers. Be exhaustive.
        """
        grounding = await self.generate(instruction=grounding_instruction, context="")

        # === PHASE 2: PROBLEM DECOMPOSITION ===
        # Break into solvable subproblems with dependencies
        decomposition_instruction = f"""
        Based on the grounded analysis:
        {grounding}

        Decompose this problem into minimal, independent subproblems. Each subproblem should be:
        - Self-contained (can be solved with given data)
        - Computationally or logically atomic
        - Clearly described with required inputs and expected output

        Identify dependencies: which subproblems must be solved before others?
        Example: "Calculate total legs from spiders" → no dependency; "Calculate time from pages" → depends on total pages.

        Return as list of subproblems with 'id', 'description', and 'dependencies'.
        """
        subproblems = await self.decompose(instruction=decomposition_instruction, context=grounding)

        # If decomposition fails or returns empty, fall back to direct solve
        if not subproblems or len(subproblems) == 0:
            fallback_instruction = """
            Solve this elementary math word problem directly. Extract all numbers and operations.
            Perform calculations step by step. Validate that the answer is reasonable (non-negative, appropriate magnitude).
            Return only the final numerical answer.
            """
            result = await self.programmer(instruction=fallback_instruction, context="")
            # Extract number from result
            match = re.search(r'[\d,]+\.?\d*', result)
            return float(match.group().replace(',', '')) if match else result

        # === PHASE 3: PARALLEL SUBPROBLEM SOLVING ===
        # Solve each subproblem in parallel, choosing appropriate solver
        async def solve_subproblem(sub):
            sub_id = sub['id']
            desc = sub['description']
            
            # Classify subproblem type to choose solver
            classification = await self.generate(
                instruction=f"""
                Classify this subproblem for optimal solving strategy:
                "{desc}"
                
                Choose ONE approach:
                - CODE: Requires arithmetic, unit conversion, iteration, or formula
                - LOGIC: Requires deduction, counting, or relational reasoning without complex math
                - HYBRID: Both
                
                Respond ONLY with the word: CODE, LOGIC, or HYBRID.
                """,
                context=""
            )
            
            if "CODE" in classification.upper():
                code_instruction = f"""
                Solve this subproblem using Python code:
                "{desc}"
                
                Use the following context from problem grounding:
                {grounding}
                
                Write minimal, safe code that computes the answer. Print only the numerical result.
                Handle units if necessary. Validate for reasonableness (e.g., no negative counts).
                """
                return await self.programmer(instruction=code_instruction, context=desc)
            else:
                logic_instruction = f"""
                Solve this subproblem using step-by-step logical reasoning:
                "{desc}"
                
                Context from problem:
                {grounding}
                
                Show your reasoning clearly. End with the final answer in the format: "ANSWER: X"
                """
                logic_result = await self.generate(instruction=logic_instruction, context=desc)
                # Extract answer from logic result
                match = re.search(r'ANSWER:\s*([\d,]+\.?\d*)', logic_result)
                if match:
                    return match.group(1)
                return logic_result  # fallback

        # Execute all subproblems in parallel
        sub_results = await asyncio.gather(*[solve_subproblem(sp) for sp in subproblems])
        sub_id_to_result = {subproblems[i]['id']: sub_results[i] for i in range(len(subproblems))}

        # === PHASE 4: SYNTHESIS & ENSEMBLE ===
        synthesis_contexts = [
            f"Subproblem {sub['id']}: {sub['description']} → Result: {sub_id_to_result[sub['id']]}"
            for sub in subproblems
        ]
        
        ensemble_instruction = """
        Synthesize all subproblem results into a final answer. Steps:
        1. Combine results according to their logical/mathematical relationships.
        2. Ensure unit consistency (convert if necessary).
        3. Validate that the final number answers the original question.
        4. Check for reasonableness: non-negative, appropriate magnitude, integer if counting discrete items.
        
        If any inconsistency is found, flag it and attempt correction.
        Output ONLY the final numerical answer.
        """
        synthesized = await self.ensemble(instruction=ensemble_instruction, contexts_list=synthesis_contexts)

        # === PHASE 5: VALIDATION & REFINEMENT ===
        refined = await self.revise(
            instruction="""
            Critically validate this solution:
            - Is the math correct? Recheck calculations.
            - Are units preserved and appropriate?
            - Is the answer non-negative and reasonable? (e.g., no 0.5 people, no 10000 hours in a week)
            - Does it directly answer the question asked?
            
            If any issue is found, revise and correct it. Otherwise, return the answer unchanged.
            Output ONLY the final numerical value.
            """,
            context=synthesized
        )

        # Extract clean numerical answer
        match = re.search(r'[\d,]+\.?\d*', refined)
        if match:
            answer_str = match.group().replace(',', '')
            # Return as int if whole number, else float
            if '.' in answer_str:
                return float(answer_str)
            else:
                return int(answer_str)
        
        # Fallback: return as-is if no number found (shouldn't happen)
        return refined