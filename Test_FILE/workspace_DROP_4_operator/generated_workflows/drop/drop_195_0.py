# Workflow ID: drop_195_0
# Benchmark: drop
# Data Indices: [302, 19]

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

        # Step 1: Extract Information
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Named entities: People, places, organizations
            - Numbers: Values and their contexts
            - Relationships: Actions, events, and their participants
            Format as structured JSON.""",
            context=""
        )

        # Step 2: Analyze the Question
        question_analysis = await self.generate(
            instruction=f"""Classify the question based on the extracted information:
            {extracted_info}
            
            Categories:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times something occurs.
            - Comparison: Greater, longer, earlier, etc.
            - Span Extraction: Exact text span answers.
            
            Provide classification and reasoning.""",
            context=extracted_info
        )

        # Step 3: Resolve References
        reference_mapping = await self.generate(
            instruction=f"""Map question references to specific entities in the passage:
            Extracted Info: {extracted_info}
            Question Analysis: {question_analysis}
            
            Resolve pronouns and partial names to specific entities.""",
            context=question_analysis
        )

        # Step 4: Execute Operations (Parallel Processing)
        arithmetic_result = await self.generate(
            instruction=f"""Perform arithmetic operations if required:
            Extracted Info: {extracted_info}
            Reference Mapping: {reference_mapping}
            
            Show calculations and final result.""",
            context=reference_mapping
        )
        counting_result = await self.generate(
            instruction=f"""Count occurrences if required:
            Extracted Info: {extracted_info}
            Reference Mapping: {reference_mapping}
            
            Show counts and final result.""",
            context=reference_mapping
        )
        comparison_result = await self.generate(
            instruction=f"""Perform comparisons if required:
            Extracted Info: {extracted_info}
            Reference Mapping: {reference_mapping}
            
            Show comparisons and final result.""",
            context=reference_mapping
        )
        span_extraction_result = await self.generate(
            instruction=f"""Extract exact text spans if required:
            Extracted Info: {extracted_info}
            Reference Mapping: {reference_mapping}
            
            Show extracted spans.""",
            context=reference_mapping
        )

        # Step 5: Ensemble Results
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the provided options:
            - Arithmetic Result: {arithmetic_result}
            - Counting Result: {counting_result}
            - Comparison Result: {comparison_result}
            - Span Extraction Result: {span_extraction_result}
            
            Choose the most appropriate answer based on the question.""",
            contexts_list=[
                arithmetic_result,
                counting_result,
                comparison_result,
                span_extraction_result
            ]
        )

        # Optional: Refine Final Answer
        refined_answer = await self.revise(
            instruction="Refine the final answer for clarity and correctness.",
            context=final_answer
        )

        return refined_answer