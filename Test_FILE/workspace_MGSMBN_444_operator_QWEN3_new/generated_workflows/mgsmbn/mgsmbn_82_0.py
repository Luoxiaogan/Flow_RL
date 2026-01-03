# Workflow ID: mgsmbn_82_0
# Benchmark: mgsmbn
# Data Indices: [102, 84]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for solving Bengali elementary math word problems.
        Combines sequential decomposition, conditional branching, parallel exploration,
        and iterative refinement to handle any problem in the domain.
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio
        import re

        # Phase 1: Problem Decomposition - Extract key information
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and extract all mathematical components. 
            Structure your response as follows:
            1. KNOWN_QUANTITIES: List all numbers mentioned with their context (what they represent)
            2. UNKNOWN_QUANTITIES: What needs to be calculated
            3. RELATIONSHIPS: Mathematical relationships between quantities (addition, subtraction, multiplication, division, ratios, etc.)
            4. UNITS: All units mentioned (টাকা, ঘণ্টা, জিনিস, etc.) and their consistency
            5. CONSTRAINTS: Any real-world constraints (non-negative values, whole numbers, etc.)
            6. PROBLEM_TYPE: Classify as one of: Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity
            Be exhaustive and precise. Don't solve yet - just extract and structure information.""",
            context=""
        )

        # Phase 2: Problem Classification and Strategy Selection
        classification = await self.generate(
            instruction=f"""Based on the decomposition:
            {decomposition}
            
            Classify this problem more precisely and select solution strategy:
            1. PRIMARY_OPERATION: What is the main mathematical operation needed? (Addition, Subtraction, Multiplication, Division, Combination)
            2. STEPS_REQUIRED: How many distinct calculation steps are needed? (1, 2, 3+)
            3. STRATEGY: Choose appropriate approach:
               - For sequential: Chronological step-by-step
               - For proportional: Set up ratio/proportion equation
               - For distribution: Division with possible remainder handling
               - For comparison: Find difference or ratio
               - For multi-entity: Track each entity separately then combine
            4. COMPLEXITY_LEVEL: Simple (direct calculation) or Complex (requires intermediate steps)
            5. AMBIGUITY_SCORE: Rate from 1-5 how ambiguous the problem is (1=clear, 5=very ambiguous)
            Provide structured classification to guide solution approach.""",
            context=decomposition
        )

        # Phase 3: Conditional Branching - Different approaches based on complexity
        if "AMBIGUITY_SCORE: 4" in classification or "AMBIGUITY_SCORE: 5" in classification:
            # High ambiguity - explore multiple solution paths in parallel
            solution_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate Solution Attempt 1 - Literal Interpretation:
                    Using the decomposition: {decomposition}
                    And classification: {classification}
                    Solve the problem by taking the most literal interpretation of the Bengali text.
                    Show all steps clearly with intermediate calculations.
                    Format: Step 1: [calculation], Step 2: [calculation], ..., Final Answer: [number]""",
                    context=decomposition
                ),
                self.generate(
                    instruction=f"""Generate Solution Attempt 2 - Contextual Interpretation:
                    Using the decomposition: {decomposition}
                    And classification: {classification}
                    Solve the problem by considering real-world context and common sense.
                    Sometimes Bengali problems imply steps not explicitly stated.
                    Show all steps clearly with intermediate calculations.
                    Format: Step 1: [calculation], Step 2: [calculation], ..., Final Answer: [number]""",
                    context=decomposition
                ),
                self.generate(
                    instruction=f"""Generate Solution Attempt 3 - Mathematical Modeling:
                    Using the decomposition: {decomposition}
                    And classification: {classification}
                    Set up formal mathematical equations based on the relationships.
                    Solve algebraically, showing all steps.
                    Format: Step 1: [equation], Step 2: [solution], ..., Final Answer: [number]""",
                    context=decomposition
                )
            )
            
            # Synthesize or select best solution
            final_solution = await self.ensemble(
                instruction="""Select the best solution from the three attempts:
                Criteria:
                1. Mathematical correctness (priority #1)
                2. Alignment with problem constraints
                3. Real-world plausibility
                4. Completeness of steps
                If multiple solutions are mathematically correct, choose the one that best fits the context.
                If solutions differ, explain why you chose one over others.
                Present the selected solution with all steps clearly shown.""",
                contexts_list=solution_attempts
            )
        else:
            # Low ambiguity - direct solution with refinement loop
            initial_solution = await self.generate(
                instruction=f"""Solve the problem using the optimal approach:
                Problem decomposition: {decomposition}
                Classification: {classification}
                
                Follow these steps:
                1. State what you're solving for
                2. Show all mathematical steps in sequence
                3. Include units at each step where applicable
                4. Verify intermediate results make sense
                5. Present final answer clearly
                Be meticulous and show your work completely.""",
                context=decomposition
            )
            
            # Validation and refinement loop (up to 2 iterations)
            current_solution = initial_solution
            for i in range(2):
                validation = await self.generate(
                    instruction=f"""Critically validate this solution:
                    {current_solution}
                    
                    Check for:
                    1. Mathematical errors in calculations
                    2. Unit consistency throughout
                    3. Violation of real-world constraints (negative quantities, fractional people when inappropriate, etc.)
                    4. Missing steps or logical gaps
                    5. Alignment with original problem requirements
                    If any issues found, describe them specifically. If no issues, state "VALIDATED".
                    Be brutally honest in your assessment.""",
                    context=current_solution
                )
                
                if "VALIDATED" in validation or "validated" in validation:
                    final_solution = current_solution
                    break
                else:
                    # Revise based on validation feedback
                    current_solution = await self.revise(
                        instruction=f"""Revise the solution based on this validation feedback:
                        {validation}
                        
                        Requirements:
                        1. Fix all identified errors
                        2. Maintain clear step-by-step format
                        3. Ensure units are consistent
                        4. Add any missing steps
                        5. Keep the solution focused on the original problem
                        Show the complete revised solution with all steps.""",
                        context=current_solution
                    )
                    final_solution = current_solution

        # Phase 4: Final Answer Extraction - Ensure single numerical output
        final_answer = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this solution:
            {final_solution}
            
            Rules:
            1. Look for phrases like "Final Answer:", "উত্তর:", "মোট", "সর্বমোট" followed by a number
            2. If multiple numbers appear, select the one that answers the main question
            3. Return ONLY the number (integer or decimal) with no additional text
            4. If the answer is fractional, convert to decimal if appropriate
            5. Ensure the number makes sense in context (not negative when inappropriate, etc.)
            Example outputs: "82", "20.5", "3", "150"
            DO NOT include any explanation, just the number.""",
            context=final_solution
        )

        # Clean the final answer (remove any accidental text)
        # Extract only digits and decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        # Handle edge case where multiple numbers might be extracted
        if '.' in cleaned_answer:
            parts = cleaned_answer.split('.')
            if len(parts) > 2:  # Multiple decimal points
                cleaned_answer = parts[0] + '.' + ''.join(parts[1:])
        
        return cleaned_answer