# Workflow ID: drop_199_0
# Benchmark: drop
# Data Indices: [145, 317]

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

        # Step 1: Extract Key Information
        entities_task = self.generate(
            instruction="""Extract all named entities (people, places, organizations) 
            and their relationships from the passage. Format as a structured list.""",
            context=""
        )
        numbers_task = self.generate(
            instruction="""Extract all numbers and their associated contexts from the passage. 
            Include units and what they represent.""",
            context=""
        )
        references_task = self.generate(
            instruction="""Identify and resolve all pronouns and partial names in the passage. 
            Map them to specific entities.""",
            context=""
        )

        # Run extraction tasks in parallel
        entities, numbers, references = await asyncio.gather(entities_task, numbers_task, references_task)

        # Step 2: Classify the Question
        classification = await self.generate(
            instruction=f"""Classify the question into one of the following categories:
            1. Arithmetic (addition, subtraction, counting)
            2. Comparison (greater than, less than, equality)
            3. Span Extraction (exact text span)
            4. Multi-Hop Reasoning (combining multiple facts)
            
            Passage Context:
            Entities: {entities}
            Numbers: {numbers}
            References: {references}""",
            context=""
        )

        # Step 3: Execute Operations Based on Classification
        if "arithmetic" in classification.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation using the numbers:
                {numbers}
                
                Ensure all calculations are precise and show intermediate steps.""",
                context=classification
            )
        elif "comparison" in classification.lower():
            result = await self.generate(
                instruction=f"""Compare the relevant values from the passage:
                {numbers}
                
                Determine which is greater, less, or equal, and explain the reasoning.""",
                context=classification
            )
        elif "span extraction" in classification.lower():
            result = await self.generate(
                instruction=f"""Locate the exact text span from the passage that answers the question.
                Ensure the span matches the question's intent exactly.""",
                context=classification
            )
        elif "multi-hop reasoning" in classification.lower():
            result = await self.generate(
                instruction=f"""Combine multiple facts from the passage to answer the question:
                Entities: {entities}
                Numbers: {numbers}
                References: {references}
                
                Resolve any intermediate references and show the reasoning chain.""",
                context=classification
            )
        else:
            result = await self.generate(
                instruction="Apply general problem-solving framework to answer the question.",
                context=classification
            )

        # Step 4: Validate and Refine
        validation = await self.revise(
            instruction=f"""Validate the result:
            {result}
            
            Ensure it matches the expected format and context. Identify any ambiguities.""",
            context=result
        )

        if "ambiguity" in validation.lower() or "error" in validation.lower():
            refined_result = await self.revise(
                instruction=f"""Refine the result based on validation feedback:
                {validation}
                
                Resolve ambiguities and correct errors.""",
                context=result
            )
            result = refined_result

        # Step 5: Ensemble Decision-Making
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer or synthesize complementary insights.",
            contexts_list=[result, validation]
        )

        return final_answer