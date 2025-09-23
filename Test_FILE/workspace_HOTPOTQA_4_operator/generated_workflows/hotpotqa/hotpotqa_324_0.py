# Workflow ID: hotpotqa_324_0
# Benchmark: hotpotqa
# Data Indices: [493, 133]

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

        # Step 1: Classify the question type and extract key components
        classification = await self.generate(
            instruction="""Classify the question type and identify key components:
            - Is it a bridge, comparison, or compositional question?
            - What entities or properties are mentioned in the question?
            - What is the expected answer format?
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Extract potential bridge entities in parallel
        entities = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract all mentions of '{entity}' from the documents.
                Include context sentences and document titles.""",
                context=classification
            ) for entity in classification.split("\n") if "entity" in entity.lower()]
        )

        # Step 3: Build the reasoning chain by connecting entities across documents
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from the extracted entities:
            - Identify connections between entities across documents.
            - Trace the logical path from the question to the answer.
            - Validate the reasoning chain against the context documents.""",
            contexts_list=entities
        )

        # Step 4: Extract and validate the precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the relevant document.
            Ensure it matches the expected answer format and is factually correct.""",
            context=reasoning_chain
        )

        # Step 5: Iterative refinement to address ambiguity or errors
        refined_answer = await self.revise(
            instruction="""Review the extracted answer:
            - Verify factual correctness.
            - Ensure alignment with the reasoning chain.
            - Address any ambiguities or inconsistencies.""",
            context=answer_extraction
        )

        return refined_answer