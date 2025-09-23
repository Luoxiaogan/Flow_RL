# Workflow ID: drop_33_0
# Benchmark: drop
# Data Indices: [190, 36]

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

        # --- EXTRACTION PHASE ---
        # Extract entities, numbers, and relationships
        extraction = await self.generate(
            instruction="""Extract all relevant information from the passage:
            - Named entities (people, places, organizations)
            - Numbers and their contexts (e.g., prices, dates)
            - Relationships between entities (e.g., who did what)
            - Resolve pronouns and references to their antecedents
            Format as a structured list.""",
            context=""
        )

        # --- CLASSIFICATION PHASE ---
        # Classify the question and identify required operations
        classification = await self.generate(
            instruction=f"""Classify the question based on the extracted information:
            {extraction}
            
            Determine:
            - Question type (arithmetic, counting, comparison, span extraction)
            - Required operation(s) (e.g., addition, subtraction, comparison)
            - Expected answer format (number, date, text span)
            Provide a clear analysis.""",
            context=extraction
        )

        # --- REASONING PHASE ---
        # Perform the identified operation(s)
        reasoning_tasks = []
        if "arithmetic" in classification.lower():
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Perform arithmetic operations based on the question:
                    {classification}
                    
                    Use the extracted numbers and relationships:
                    {extraction}
                    
                    Show all steps and provide the final result.""",
                    context=classification
                )
            )
        elif "counting" in classification.lower():
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Count instances based on the question:
                    {classification}
                    
                    Use the extracted entities and relationships:
                    {extraction}
                    
                    Provide the total count.""",
                    context=classification
                )
            )
        elif "comparison" in classification.lower():
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Compare values based on the question:
                    {classification}
                    
                    Use the extracted numbers and relationships:
                    {extraction}
                    
                    State which is greater/longer/more and why.""",
                    context=classification
                )
            )
        elif "span extraction" in classification.lower():
            reasoning_tasks.append(
                self.generate(
                    instruction=f"""Extract the exact text span that answers the question:
                    {classification}
                    
                    Use the extracted entities and relationships:
                    {extraction}
                    
                    Ensure the span matches the passage exactly.""",
                    context=classification
                )
            )

        # Execute reasoning tasks in parallel
        reasoning_results = await asyncio.gather(*reasoning_tasks)

        # --- VALIDATION PHASE ---
        # Validate and format the answer
        validation = await self.ensemble(
            instruction="""Validate the reasoning results:
            - Ensure the answer matches the expected format
            - Cross-check with constraints from the question
            - Select the best result if multiple options exist
            Provide the final answer.""",
            contexts_list=reasoning_results
        )

        return validation