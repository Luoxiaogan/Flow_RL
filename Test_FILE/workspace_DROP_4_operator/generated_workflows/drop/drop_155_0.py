# Workflow ID: drop_155_0
# Benchmark: drop
# Data Indices: [88, 491]

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
        
        # Step 1: Initial Information Extraction
        extraction_instruction = """
        Extract all named entities, numbers, dates, and relationships from the passage.
        Resolve references such as pronouns and partial names to their respective entities.
        Format the extracted information in a structured list:
        - Entities: [names and roles]
        - Numbers: [values and what they represent]
        - Dates: [dates and their contexts]
        - Relationships: [connections between entities]
        """
        extracted_info = await self.generate(instruction=extraction_instruction, context="")
        
        # Step 2: Problem Classification and Operation Identification
        classification_instruction = f"""
        Classify the problem based on the provided question:
        - Determine if it requires arithmetic (addition, subtraction), counting, comparison, or span extraction.
        - Identify the specific operation(s) needed.
        - Consider the following examples:
          * "How many total": Addition
          * "How many more": Subtraction
          * "Which is greater": Comparison
          * "Who did": Span extraction
        
        Extracted Information:
        {extracted_info}
        """
        classification_result = await self.generate(instruction=classification_instruction, context=extracted_info)
        
        # Step 3: Execution of Identified Operations
        execution_instruction = f"""
        Execute the identified operations using the extracted information.
        Ensure all instances of relevant data are considered.
        Perform the operations accurately and provide intermediate results.
        
        Classification Result:
        {classification_result}
        
        Extracted Information:
        {extracted_info}
        """
        execution_result = await self.generate(instruction=execution_instruction, context=f"{classification_result}\n{extracted_info}")
        
        # Step 4: Answer Validation and Refinement
        validation_instruction = f"""
        Validate the computed result against the expected format.
        Refine the result if necessary to match the required format (number, date, exact text span).
        
        Execution Result:
        {execution_result}
        """
        refined_result = await self.revise(instruction=validation_instruction, context=execution_result)
        
        # Step 5: Final Output
        final_instruction = f"""
        Condense the refined result into a concise output that meets the answer format requirements.
        Ensure the final answer is clear and matches the expected format.
        
        Refined Result:
        {refined_result}
        """
        final_answer = await self.summarize(instruction=final_instruction, context=refined_result)
        
        return final_answer