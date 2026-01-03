# Workflow ID: hotpotqa_201_0
# Benchmark: hotpotqa
# Data Indices: [480]

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
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (comparing properties)?
            3. Is it a compositional question (combining facts)?
            
            Extract potential bridge entities or properties from the documents. 
            Provide structured classification and extracted entities.""",
            context=""
        )

        # Step 2: Entity Identification - Identify relevant entities/properties
        entities = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Identify specific entities or properties relevant to the question:
            - For bridge questions, find shared entities between documents.
            - For comparison questions, extract comparable properties.
            - For compositional questions, gather relevant facts from multiple documents.
            
            Ensure each entity/property is linked to its source document.""",
            context=analysis
        )

        # Step 3: Parallel Processing - Construct reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain using the entity/property:
                {entity}
                
                Link this entity/property across documents to form a coherent chain leading to the answer.
                Ensure each step in the chain is factually supported by the documents.""",
                context=entities
            ) for entity in entities.split('\n') if entity.strip()]
        )

        # Step 4: Ensemble Selection - Choose the best reasoning chain
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain that leads to the answer.",
            contexts_list=reasoning_chains
        )

        # Step 5: Answer Extraction - Extract precise answer
        answer = await self.generate(
            instruction=f"""Using the selected reasoning chain:
            {best_chain}
            
            Extract the precise answer from the final document in the chain.
            Ensure the answer is concise and directly addresses the question.""",
            context=best_chain
        )

        # Step 6: Validation and Refinement - Critique and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Critique and refine the extracted answer:
            {answer}
            
            Ensure the answer is factually correct, concise, and directly addresses the question.
            If necessary, adjust based on supporting facts from the documents.""",
            context=answer
        )

        return refined_answer