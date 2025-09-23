# Workflow ID: hotpotqa_124_0
# Benchmark: hotpotqa
# Data Indices: [29, 495]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        classification_task = self.generate(
            instruction="""Classify the question type:
            - Bridge: Connects entities across documents
            - Comparison: Evaluates properties across documents
            - Compositional: Combines multiple facts
            Provide a clear classification.""",
            context=""
        )
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract key entities, relationships, and facts from Document {i+1}.
                Focus on proper nouns, dates, and significant phrases. Format as structured list.""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        classification, entities = await asyncio.gather(classification_task, *entity_extraction_tasks)

        # Step 2: Entity Linking and Document Matching
        entity_mapping = await self.ensemble(
            instruction="""Map entities to documents and identify shared entities.
            Shared entities are potential bridge entities.""",
            contexts_list=entities
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Based on the question classification:
            {classification}
            
            And the entity mapping:
            {entity_mapping}
            
            Construct a reasoning chain that connects the question to a potential answer.
            Follow shared entities or evaluate properties as needed.""",
            context=""
        )

        # Step 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the exact answer span from the final document in the chain.
            Ensure the answer is factually correct and matches the question.""",
            context=""
        )

        # Step 5: Iterative Refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Cross-reference with supporting facts from the documents.
            Identify any discrepancies or missing links.""",
            context=""
        )
        if "discrepancy" in validation.lower() or "missing" in validation.lower():
            refined_chain = await self.revise(
                instruction=f"""Refine the reasoning chain based on validation feedback:
                {validation}""",
                context=reasoning_chain
            )
            refined_answer = await self.generate(
                instruction=f"""Extract the refined answer from the updated reasoning chain:
                {refined_chain}""",
                context=""
            )
            return refined_answer

        return answer_extraction