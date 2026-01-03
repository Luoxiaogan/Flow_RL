# Workflow ID: mgsmbn_71_0
# Benchmark: mgsmbn
# Data Indices: [129, 147]

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
        
        # PHASE 1: PROBLEM DIAGNOSIS
        diagnosis = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem and classify it along these dimensions:
            1. Problem Type: Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity, or Other
            2. Complexity Level: Simple (1-2 steps), Medium (3-4 steps), Complex (5+ steps or hidden dependencies)
            3. Entity Count: Number of distinct people/objects with quantities
            4. Operation Types: List required operations (addition, subtraction, multiplication, division, algebra, etc.)
            5. Unit Handling: Are units consistent? Need conversion? (টাকা, ঘণ্টা, জিনিস, etc.)
            6. Constraints: Any real-world constraints? (no negative items, whole people only, etc.)
            7. Hidden Steps: Are there implicit calculations not directly stated?
            
            Format your response as a structured analysis with clear section headers for each dimension above.
            Be conservative in complexity assessment - only mark as Complex if truly necessary.""",
            context=""
        )
        
        # PHASE 2: ADAPTIVE ROUTING
        is_simple = "Simple" in diagnosis and ("addition" in diagnosis.lower() or "subtraction" in diagnosis.lower()) and "1" in diagnosis
        has_multiple_entities = "Multi-entity" in diagnosis or int(re.search(r'Entity Count:\s*(\d+)', diagnosis).group(1)) > 1 if re.search(r'Entity Count:\s*(\d+)', diagnosis) else False
        
        if is_simple and not has_multiple_entities:
            # Direct solve for simple arithmetic problems
            solution = await self.programmer(
                instruction="""Solve this simple arithmetic problem directly.
                Extract the numbers and operation from the Bengali text.
                Perform the calculation.
                Return only the numerical result.
                Example: For "11 + 6 - 2", return "15".""",
                context=diagnosis
            )
        else:
            # Complex problem - use diamond pattern with validation
            # Generate three parallel solution approaches
            algebraic_approach = self.generate(
                instruction="""Solve using algebraic modeling:
                1. Define variables for unknowns
                2. Translate Bengali relationships into equations
                3. Solve the system step by step
                4. Show all work and final answer
                Focus on mathematical rigor and symbolic representation.""",
                context=diagnosis
            )
            
            chronological_approach = self.generate(
                instruction="""Solve chronologically as events unfold:
                1. Identify sequence of events in the narrative
                2. Calculate changes at each step
                3. Maintain running totals
                4. Show timeline of calculations
                Think like a story - what happens first, then next, then finally.""",
                context=diagnosis
            )
            
            tabular_approach = self.generate(
                instruction="""Solve using tabular representation:
                1. Create a table with entities as rows and time/events as columns
                2. Fill in known values
                3. Calculate missing cells
                4. Derive final answer from table
                Good for multi-entity problems with changing quantities over time.""",
                context=diagnosis
            )
            
            # Execute in parallel
            approaches = await asyncio.gather(
                algebraic_approach,
                chronological_approach,
                tabular_approach
            )
            
            # Ensemble the approaches
            solution = await self.ensemble(
                instruction="""Synthesize the three solution approaches into one definitive answer:
                1. Compare results from all three methods
                2. If all agree, select that answer
                3. If there's disagreement, identify which approach best handles the problem's constraints
                4. Apply real-world validation: no negative counts, whole people, etc.
                5. Return only the final numerical answer as a string""",
                contexts_list=approaches
            )
            
            # Validate by working backwards
            validation = await self.generate(
                instruction=f"""Validate by reverse engineering:
                Assume the answer is {solution}.
                Work backwards through the problem to reconstruct the initial conditions.
                Does this match the original problem statement?
                If not, explain the discrepancy and provide corrected answer.
                If yes, simply return the original answer: {solution}""",
                context=f"Original Diagnosis: {diagnosis}\n\nSolution: {solution}"
            )
            
            # Extract final answer from validation (in case it was corrected)
            solution = validation
        
        # Final sanitization - extract only the number
        final_answer = await self.generate(
            instruction=f"""Extract only the numerical answer from the following text.
            Remove any units, explanations, or additional text.
            Return just the number, as a string.
            If multiple numbers, return the final answer.
            Input: {solution}""",
            context=""
        )
        
        # Clean the answer (remove any remaining non-numeric characters except decimal point)
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer)
        
        return cleaned_answer