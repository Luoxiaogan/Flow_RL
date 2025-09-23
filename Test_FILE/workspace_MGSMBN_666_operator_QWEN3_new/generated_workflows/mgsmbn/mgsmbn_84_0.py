# Workflow ID: mgsmbn_84_0
# Benchmark: mgsmbn
# Data Indices: [100, 179]

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

        # STEP 1: Semantic Decomposition - Extract entities, actions, states, constraints
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math problem. Identify:
            1. All entities (people, objects, groups) and their roles
            2. All quantities (explicit and implicit) and what they represent
            3. All actions (verbs) and their temporal/causal sequence
            4. All constraints (physical, logical, contextual)
            5. The unknown being asked for
            6. Any fractional, proportional, or comparative relationships
            Present as structured narrative with clear labeling. Think step by step.""",
            context=""
        )

        # STEP 2: Generate three independent problem-type classifications in parallel
        classification_tasks = [
            self.generate(
                instruction=f"""Analyze this problem type based on decomposition:
                {decomposition[:1000]}...
                
                Classify into one primary category:
                A. Direct Calculation (explicit operations, no unknowns beyond final answer)
                B. Algebraic Modeling (requires solving for unknowns with equations)
                C. Reverse Simulation (final state given, must work backwards)
                
                Justify your classification with 2-3 specific reasons from the decomposition.
                Be precise and critical.""",
                context=""
            ) for _ in range(3)
        ]
        
        classifications = await asyncio.gather(*classification_tasks)
        
        # STEP 3: Ensemble to determine dominant problem type
        problem_type = await self.ensemble(
            instruction="""Determine the most accurate problem classification from these three analyses.
            Consider:
            - Consistency with the semantic decomposition
            - Mathematical soundness of reasoning
            - Alignment with problem's narrative structure
            - Handling of edge cases or ambiguities
            
            Output only the letter (A, B, or C) of the best classification.""",
            contexts_list=classifications
        )

        # STEP 4: Route to appropriate solution path with dynamically generated instructions
        solution = None
        validation_needed = True
        
        for attempt in range(2):  # Allow one re-attempt if validation fails
            if "A" in problem_type.upper():
                # Direct Calculation Path
                solution = await self.programmer(
                    instruction=f"""Solve this Bengali math problem using direct calculation:
                    Decomposition context: {decomposition[:1500]}
                    
                    Steps:
                    1. Extract all given numbers and their meanings
                    2. Identify sequence of operations from narrative
                    3. Perform calculations step by step
                    4. Track units throughout
                    5. Output final numerical answer only
                    
                    Important: No algebra needed. Just arithmetic in narrative order.
                    Validate intermediate results make sense in context.""",
                    context=decomposition
                )
                
            elif "B" in problem_type.upper():
                # Algebraic Modeling Path
                solution = await self.programmer(
                    instruction=f"""Solve this Bengali math problem using algebraic modeling:
                    Decomposition context: {decomposition[:1500]}
                    
                    Steps:
                    1. Define variables for unknowns (use meaningful names)
                    2. Translate relationships into equations
                    3. Solve system step by step
                    4. Substitute known values
                    5. Output final numerical answer only
                    
                    Important: Show symbolic work before numeric substitution.
                    Check for extraneous solutions.""",
                    context=decomposition
                )
                
            else:  # "C" - Reverse Simulation Path
                solution = await self.programmer(
                    instruction=f"""Solve this Bengali math problem using reverse simulation:
                    Decomposition context: {decomposition[:1500]}
                    
                    Steps:
                    1. Start from final known state
                    2. Invert each operation in reverse chronological order
                    3. Handle fractions/proportions carefully (invert denominators)
                    4. Validate intermediate states are non-negative and realistic
                    5. Output final numerical answer only
                    
                    Important: Work backwards from end to beginning.
                    Double-check inversion of operations (e.g., 1/3 becomes *3).""",
                    context=decomposition
                )

            if not validation_needed:
                break
                
            # STEP 5: Parallel Validation - Narrative and Mathematical
            validation_tasks = [
                self.generate(
                    instruction=f"""Narrative Validation:
                    Problem: {self.problem_text[:500]}
                    Proposed Solution: {solution[:500]}
                    Decomposition: {decomposition[:500]}
                    
                    Does this answer make sense in the story?
                    - Are quantities realistic (no negative people, fractional items if inappropriate)?
                    - Does the sequence of events logically lead to this result?
                    - Are units consistent throughout?
                    Answer YES or NO with brief justification.""",
                    context=solution
                ),
                self.generate(
                    instruction=f"""Mathematical Boundary Validation:
                    Problem: {self.problem_text[:500]}
                    Proposed Solution: {solution[:500]}
                    Decomposition: {decomposition[:500]}
                    
                    Check:
                    - Are all mathematical operations correctly applied?
                    - Are fractions/proportions handled properly?
                    - Does answer satisfy all constraints from decomposition?
                    - Is there any calculation error?
                    Answer YES or NO with brief justification.""",
                    context=solution
                )
            ]
            
            narrative_val, math_val = await asyncio.gather(*validation_tasks)
            
            if "YES" in narrative_val.upper() and "YES" in math_val.upper():
                validation_needed = False
                break
            else:
                # Trigger re-decomposition with different perspective
                decomposition = await self.revise(
                    instruction=f"""Previous decomposition may have misinterpreted key relationships.
                    Focus especially on: {narrative_val} and {math_val}
                    Re-analyze with emphasis on potentially misread phrases or operations.
                    Consider alternative interpretations of fractional/comparative language.
                    Maintain all previous good insights but correct identified flaws.""",
                    context=decomposition
                )
                # Re-classify problem type after revised decomposition
                classifications = await asyncio.gather(*[
                    self.generate(
                        instruction=f"""Re-classify problem based on revised decomposition:
                        {decomposition[:1000]}...
                        Same criteria as before: A (Direct), B (Algebraic), C (Reverse)""",
                        context=""
                    ) for _ in range(3)
                ])
                problem_type = await self.ensemble(
                    instruction="Re-determine best classification based on revised analyses. Output A, B, or C.",
                    contexts_list=classifications
                )

        # STEP 6: Extract clean numerical answer
        final_answer = await self.generate(
            instruction=f"""Extract ONLY the final numerical answer from this solution:
            {solution[:1000]}
            
            Rules:
            - If multiple numbers, select the one answering the original question
            - Remove all units, explanations, and text
            - Return only digits, decimal points, or negative signs
            - If answer is fractional, convert to decimal
            - If no clear answer, return "0" as fallback""",
            context=solution
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point and minus sign
        cleaned = re.sub(r'[^0-9\.\-]', '', final_answer.strip())
        
        # Handle edge cases
        if not cleaned or cleaned == '.' or cleaned == '-':
            cleaned = "0"
            
        return cleaned