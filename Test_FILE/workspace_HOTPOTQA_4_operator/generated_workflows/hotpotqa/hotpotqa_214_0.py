# Workflow ID: hotpotqa_214_0
# Benchmark: hotpotqa
# Data Indices: [431, 66]

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

        # Step 1: Classify the question
        question_analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify main entities and relationships mentioned in the question.
            - Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Extract entities and relationships from documents
        documents = self.problem_text.split("**QUESTION:**")[0].split("Document ")[1:]
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract named entities, relationships, and key facts from this document:
                - Focus on entities related to the question.
                - Include relationships between entities.
                - Format as structured list.""",
                context=doc
            )
            for doc in documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Build reasoning chains
        reasoning_chain = await self.generate(
            instruction=f"""Using the question analysis and extracted entities:
            {question_analysis}
            {extracted_entities}
            
            Build a reasoning chain:
            - Identify bridge entities connecting documents.
            - Follow logical connections to derive the answer.
            - Validate each step against the context.""",
            context=""
        )

        # Refine reasoning chain
        refined_chain = await self.revise(
            instruction="""Refine the reasoning chain:
            - Ensure all steps are logically valid.
            - Add missing details or clarify ambiguous points.
            - Cross-reference with original documents for accuracy.""",
            context=reasoning_chain
        )

        # Step 4: Extract the final answer
        final_answer = await self.generate(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the precise answer:
            - Ensure it is factual and concise.
            - Directly supported by evidence from the documents.""",
            context=""
        )

        # Step 5: Validate and summarize
        validation = await self.generate(
            instruction=f"""Validate the final answer:
            - Check against the original question and supporting facts.
            - Ensure all reasoning steps are accurate.
            - Flag any inconsistencies or missing information.""",
            context=final_answer
        )

        summary = await self.summarize(
            instruction="Summarize the reasoning process and final answer.",
            context=f"{refined_chain}

{validation}"
        )

        return summary