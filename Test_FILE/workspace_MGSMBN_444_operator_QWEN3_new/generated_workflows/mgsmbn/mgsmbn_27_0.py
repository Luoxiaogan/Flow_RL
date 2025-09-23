# Workflow ID: mgsmbn_27_0
# Benchmark: mgsmbn
# Data Indices: [121, 17]

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

        # STEP 1: SEMANTIC DECOMPOSITION - Extract entities, quantities, relationships
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math problem. Extract:
            1. All named entities (people, objects, places) and their roles
            2. All numerical values and what they represent (with units)
            3. All actions/events in chronological order
            4. All explicit and implicit relationships between entities
            5. The ultimate unknown we need to solve for
            6. Any real-world assumptions required (e.g., age differences are constant, prices are per unit)
            Format as a structured markdown list with clear section headers.""",
            context=""
        )

        # STEP 2: PARALLEL MODELING - Generate 3 different mathematical interpretations
        modeling_instructions = [
            """Based on the decomposition, create Mathematical Model A:
            - Focus on direct translation of actions into operations
            - Assume literal interpretation of all phrases
            - Use algebraic expressions where possible
            - Show step-by-step equation building""",
            
            """Based on the decomposition, create Mathematical Model B:
            - Focus on proportional/rate relationships
            - Consider alternative interpretations of ambiguous phrases
            - Use ratio/fraction approaches where applicable
            - Show how quantities relate to each other""",
            
            """Based on the decomposition, create Mathematical Model C:
            - Focus on constraint-based reasoning
            - Consider edge cases and boundary conditions
            - Use logical deduction for implicit relationships
            - Show how assumptions affect the solution"""
        ]

        models = await asyncio.gather(
            self.generate(instruction=modeling_instructions[0], context=decomposition),
            self.generate(instruction=modeling_instructions[1], context=decomposition),
            self.generate(instruction=modeling_instructions[2], context=decomposition)
        )

        # STEP 3: ENSEMBLE SYNTHESIS - Merge best aspects of all models
        synthesized_model = await self.ensemble(
            instruction="""Synthesize the three mathematical models into one unified approach:
            1. Compare the models for consistency with the original problem
            2. Identify which model handles edge cases best
            3. Combine the most robust elements from each
            4. Resolve any contradictions between models
            5. Produce a single, coherent mathematical framework for solving the problem
            6. Include explicit step-by-step calculation plan
            Output should be a clear, executable mathematical procedure.""",
            contexts_list=models
        )

        # STEP 4: INITIAL SOLUTION ATTEMPT
        initial_solution = await self.generate(
            instruction="""Execute the synthesized mathematical model:
            - Perform all calculations step by step
            - Show intermediate results
            - Maintain unit tracking throughout
            - Double-check arithmetic at each step
            - Present final answer with appropriate units and context""",
            context=synthesized_model
        )

        # STEP 5: VALIDATION & REVISION LOOP (max 2 iterations)
        current_solution = initial_solution
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Perform rigorous validation of this solution:
                1. Unit Consistency: Are all units compatible and properly converted?
                2. Arithmetic Accuracy: Recalculate key steps independently
                3. Contextual Plausibility: Does the answer make sense in real-world context?
                4. Constraint Satisfaction: Are all problem constraints met?
                5. Edge Case Handling: What if inputs were slightly different?
                6. Alternative Verification: Can you verify using a different method?
                If any issues found, list them specifically. If no issues, state 'VALIDATED'.""",
                context=current_solution
            )

            if "VALIDATED" in validation or "validated" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    Validation Issues: {validation}
                    Requirements:
                    - Fix all identified issues
                    - Maintain clear step-by-step reasoning
                    - Show before/after for corrected steps
                    - Ensure final answer is numerically precise
                    - Preserve unit tracking throughout""",
                    context=current_solution
                )

        # STEP 6: ANSWER EXTRACTION - Isolate final numerical value
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution:
            - Must be a single number (integer or decimal)
            - Remove all units, text, and explanations
            - If multiple numbers, select the one that answers the original question
            - If no clear number, return 0
            - Format as plain number with no additional characters""",
            context=current_solution
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer)
        
        # Handle edge case where no number was extracted
        if not cleaned_answer:
            return "0"
            
        # Convert to float then to int if whole number, otherwise keep as float string
        try:
            num = float(cleaned_answer)
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        except:
            return "0"