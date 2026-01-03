# Workflow ID: mgsmbn_58_0
# Benchmark: mgsmbn
# Data Indices: [107]

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

        # STEP 1: PARALLEL SEMANTIC EXTRACTION
        # Generate three perspectives: literal, contextual, unit-aware
        extraction_tasks = [
            self.generate(
                instruction="""Perform LITERAL extraction:
                - Identify every number and its associated entity (e.g., '2 বার' → rides: 2)
                - List all named actors (Pam, Fred, etc.)
                - Extract explicit operations (costs 6 tickets per ride)
                - Do NOT infer, only extract what's directly stated.
                Format as JSON-like key-value pairs.""",
                context=""
            ),
            self.generate(
                instruction="""Perform CONTEXTUAL inference:
                - What do pronouns refer to? (তারা = Pam and Fred)
                - What does 'প্রত্যেকে 2 বার' imply? (each person, not total)
                - Are there implicit constraints? (tickets can't be negative)
                - What is the final question asking for?
                Format as structured natural language with inferences marked.""",
                context=""
            ),
            self.generate(
                instruction="""Perform UNIT & DIMENSION analysis:
                - What are the units involved? (tickets, rides, times)
                - What conversions are needed? (rides → tickets)
                - Are units consistent? (all in tickets? all in rides?)
                - Flag any unit mismatches or missing conversions.
                Format as bullet points with unit mappings.""",
                context=""
            )
        ]
        
        literal_extract, contextual_inference, unit_analysis = await asyncio.gather(*extraction_tasks)

        # STEP 2: ENSEMBLE INTO COHERENT MODEL
        mathematical_model = await self.ensemble(
            instruction="""Synthesize into a unified mathematical model:
            - Combine literal numbers with contextual meaning
            - Resolve unit conversions (e.g., 1 ride = 6 tickets)
            - Define the target variable (what are we solving for?)
            - Specify the calculation steps in order
            - Output as a clear, step-by-step plan with formulas.
            Prioritize interpretations that preserve unit consistency and chronological logic.""",
            contexts_list=[literal_extract, contextual_inference, unit_analysis]
        )

        # STEP 3: PROBLEM TYPE CLASSIFICATION & BRANCHING
        problem_type = await self.generate(
            instruction=f"""Classify problem type based on model:
            Model: {mathematical_model}
            
            Categories:
            - RATE (involves per-unit, speed, time)
            - DISTRIBUTION (sharing, dividing, remainders)
            - COMPARISON (differences, "how many more")
            - MULTI-ENTITY (multiple actors with different quantities)
            - SEQUENTIAL (events in order, deposits/withdrawals)
            
            Also flag:
            - Requires algebra? (solve for x)
            - Discrete entities? (people, tickets - must be integers)
            - Fractional results acceptable? (money vs. people)
            
            Output: Single line with primary type and flags.""",
            context=mathematical_model
        )

        # STEP 4: GENERATE & VALIDATE SOLUTION CODE
        solution_code = None
        final_answer = None
        
        for attempt in range(3):  # Max 3 retries
            # Generate pseudocode plan
            pseudocode = await self.generate(
                instruction=f"""Generate Python pseudocode to solve:
                Problem Type: {problem_type}
                Mathematical Model: {mathematical_model}
                
                Requirements:
                - Handle discrete entities (round down if needed)
                - Track units (convert rides to tickets)
                - Chronological order if sequential
                - Output only the final number (no text, no units)
                - Include validation checks (no negative tickets, etc.)
                
                Write as clear, commented Python code.""",
                context=mathematical_model
            )
            
            # Revise for edge cases
            revised_code = await self.revise(
                instruction=f"""Improve code:
                - Add checks for discrete entities (if problem involves people/tickets, ensure integer output)
                - Validate unit conversions (rides * 6 = tickets)
                - Handle edge cases (zero values, negative results)
                - Ensure output is ONLY a number (int or float)
                - Add comments explaining each step
                Problem Type Flags: {problem_type}""",
                context=pseudocode
            )
            
            # Execute code
            try:
                execution_result = await self.programmer(
                    instruction="Execute this code to solve the problem. Return only the numerical result.",
                    context=revised_code,
                    max_retries=1
                )
                
                # Extract number from result (sometimes Programmer adds text)
                number_match = re.search(r'[-+]?\d*\.\d+|\d+', execution_result)
                if number_match:
                    final_answer = number_match.group(0)
                    # Validate answer makes sense
                    validation = await self.generate(
                        instruction=f"""Validate answer: {final_answer}
                        - Is it positive? (unless debt is allowed)
                        - Is it integer if entities are discrete?
                        - Is magnitude reasonable? (e.g., not 1000 tickets for 2 kids)
                        - Does it match the problem's scale?
                        Return 'VALID' or 'INVALID: reason'""",
                        context=f"Problem: {self.problem_text}
Model: {mathematical_model}
Answer: {final_answer}"
                    )
                    
                    if "VALID" in validation:
                        break
                    else:
                        # Revise with validation feedback
                        pseudocode = await self.revise(
                            instruction=f"Fix issues: {validation}. Regenerate code.",
                            context=revised_code
                        )
                else:
                    raise ValueError("No number found in result")
                    
            except Exception as e:
                if attempt == 2:  # Last attempt
                    raise e
                continue

        # STEP 5: FINAL SANITIZATION
        sanitized_answer = await self.summarize(
            instruction="""Extract ONLY the numerical answer:
            - Remove any units (টাকা, টিকিট, etc.)
            - Remove any text or explanations
            - If decimal, keep full precision unless context implies rounding
            - Output must be a single number (int or float)
            Example: '60 tickets' → '60'""",
            context=str(final_answer)
        )

        # Clean any remaining non-numeric characters
        clean_answer = re.sub(r'[^\d.-]', '', sanitized_answer)
        
        return clean_answer