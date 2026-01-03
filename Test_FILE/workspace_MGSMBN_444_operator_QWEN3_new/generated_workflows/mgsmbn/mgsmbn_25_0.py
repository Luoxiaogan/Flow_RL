# Workflow ID: mgsmbn_25_0
# Benchmark: mgsmbn
# Data Indices: [78]

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

        # Step 1: Lightweight problem classification to determine depth and strategy
        classification = await self.generate(
            instruction="""Analyze this Bengali math word problem and classify it along these dimensions:
            1. Complexity Level: Simple (single operation), Medium (2-3 sequential steps), Complex (hidden steps, proportions, or constraints)
            2. Primary Reasoning Type: Arithmetic, Temporal (before/after), Proportional, Distribution, or Comparison
            3. Key Entities: List all actors/objects with their initial quantities
            4. Actions: Sequence of operations affecting quantities (add, remove, distribute, compare)
            5. Units: All units involved (টাকা, ঘণ্টা, জিনিস, etc.) and whether conversion is needed
            6. Expected Answer Type: Integer or Decimal
            7. Red Flags: Any potential distractors, ambiguities, or real-world constraints (e.g., no negative items)
            
            Format your response as a structured bullet list with clear headings for each dimension.""",
            context=""
        )

        # Step 2: Parallel solution generation using three distinct reasoning strategies
        arithmetic_strategy = asyncio.create_task(self.generate(
            instruction=f"""Solve using direct arithmetic modeling:
            - Extract all numerical values and their relationships
            - Build a mathematical expression representing the entire problem
            - Execute calculations step by step, showing intermediate results
            - Validate that units are consistent throughout
            - Return only the final numerical answer, no explanation
            
            Use this classification context: {classification}""",
            context=""
        ))

        narrative_strategy = asyncio.create_task(self.generate(
            instruction=f"""Solve using narrative timeline tracking:
            - Map the story chronologically: initial state → each action → final state
            - For each action, explicitly state what changes and by how much
            - Track entity inventories (e.g., Mary's plant pots) through each step
            - Ensure no step violates real-world constraints (no negative quantities, etc.)
            - Return only the final numerical answer, no explanation
            
            Use this classification context: {classification}""",
            context=""
        ))

        constraint_strategy = asyncio.create_task(self.generate(
            instruction=f"""Solve using constraint satisfaction:
            - Identify the final unknown quantity to solve for
            - List all constraints from the problem (explicit and implicit)
            - Set up equations or inequalities representing these constraints
            - Solve systematically, showing substitution steps
            - Verify solution satisfies all constraints
            - Return only the final numerical answer, no explanation
            
            Use this classification context: {classification}""",
            context=""
        ))

        # Gather parallel solutions
        solutions = await asyncio.gather(arithmetic_strategy, narrative_strategy, constraint_strategy)

        # Step 3: Revise each solution for internal consistency and unit validation
        revised_solutions = []
        for i, sol in enumerate(solutions):
            revised = await self.revise(
                instruction=f"""Critically revise this solution:
                - Verify all arithmetic operations are correct
                - Ensure units are consistent and properly handled
                - Check that the answer is non-negative and realistic
                - Confirm it matches the problem's final question
                - If any step is invalid, correct it and explain the fix
                - Return ONLY the final corrected numerical answer, nothing else
                
                Original solution attempt: {sol}""",
                context=sol
            )
            revised_solutions.append(revised)

        # Step 4: Ensemble — Synthesize or select best answer
        final_answer = await self.ensemble(
            instruction="""You are given three independently derived numerical answers to the same Bengali math word problem.
            Your task:
            1. Compare all three answers.
            2. If all agree, return that number.
            3. If two agree and one differs, return the majority answer.
            4. If all differ, select the answer that best satisfies:
               - Matches the problem's narrative flow
               - Maintains unit consistency
               - Produces a non-negative, realistic result
               - Aligns with the classification's complexity level
            5. Return ONLY the final selected numerical value. No explanation, no units, no text.
            
            IMPORTANT: Your output must be a single number that can be directly compared to the expected answer.""",
            contexts_list=revised_solutions
        )

        # Step 5: Final validation — ensure answer is clean numerical value
        validated_answer = await self.revise(
            instruction="""Extract ONLY the numerical value from the following text. 
            Remove any units, explanations, or formatting. 
            If the value is decimal, preserve decimal places. 
            If multiple numbers appear, select the one that answers the problem's final question.
            Return ONLY the number, nothing else.""",
            context=final_answer
        )

        # Clean and return
        # Strip any remaining non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', validated_answer.strip())
        
        # Handle edge case where no number was extracted
        if not cleaned:
            # Fallback: return 0 (though this should rarely happen)
            return "0"
            
        return cleaned