# Workflow ID: hotpotqa_20_0
# Benchmark: hotpotqa
# Data Indices: [175]

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

        # Step 1: Classify question type and extract key entities
        classification = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities involved. Provide structured output:
            - Question Type: [bridge/comparison/compositional]
            - Key Entities: [list of entities and their roles]""",
            context=""
        )

        # Step 2: Parallel document filtering and entity matching
        entities = classification.split("Key Entities:")[-1].strip()
        doc_filtering, entity_matching = await asyncio.gather(
            self.generate(
                instruction=f"""Filter documents containing the following entities: {entities}.
                For each document, list the sentences mentioning these entities.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Find bridge entities or shared properties between the following entities: {entities}.
                Provide a list of connections and their supporting evidence.""",
                context=classification
            )
        )

        # Step 3: Construct reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the filtered documents and entity connections, construct a reasoning chain:
            Filtered Documents: {doc_filtering}
            Entity Connections: {entity_matching}
            
            Provide a step-by-step explanation of how the facts lead to the answer.""",
            context=f"{doc_filtering}\n{entity_matching}"
        )

        # Step 4: Extract and validate answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            
            Provide the exact answer span.""",
            context=reasoning_chain
        )
        validation = await self.revise(
            instruction=f"""Validate the following answer:
            Answer: {answer_extraction}
            
            Ensure it is factually correct and supported by the documents.""",
            context=reasoning_chain
        )

        # Iterative refinement if validation fails
        if "error" in validation.lower() or "incorrect" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Revise the answer based on validation feedback:
                Feedback: {validation}
                
                Provide the corrected answer.""",
                context=answer_extraction
            )
            return refined_answer

        return answer_extraction