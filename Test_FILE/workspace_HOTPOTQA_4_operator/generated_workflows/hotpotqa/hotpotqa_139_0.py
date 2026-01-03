# Workflow ID: hotpotqa_139_0
# Benchmark: hotpotqa
# Data Indices: [316]

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

        # Phase 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify the question type:
            - Is it a bridge, comparison, or compositional question?
            - What are the key entities and relationships?
            - What is the expected answer format?""",
            context=""
        )

        # Phase 2: Entity and Relationship Extraction
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        entity_extraction_tasks = [
            self.generate(
                instruction=f"""Extract entities and relationships from the following document:
                {doc}
                Focus on entities mentioned in the question and their connections.""",
                context=initial_analysis
            )
            for doc in documents
        ]
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Synthesize extracted entities into a unified knowledge graph
        knowledge_graph = await self.ensemble(
            instruction="Combine extracted entities and relationships into a unified knowledge graph.",
            contexts_list=extracted_entities
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain using the knowledge graph:
            {knowledge_graph}
            Ensure the chain connects the question to the answer across documents.""",
            context=initial_analysis
        )

        # Iteratively refine the reasoning chain
        for _ in range(3):  # Allow up to 3 refinement iterations
            refined_chain = await self.revise(
                instruction="Refine the reasoning chain for logical consistency and completeness.",
                context=reasoning_chain
            )
            if "error" not in refined_chain.lower():
                reasoning_chain = refined_chain
                break

        # Phase 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span from the final document:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer aligns with the supporting facts.""",
            context=knowledge_graph
        )

        final_answer = await self.summarize(
            instruction="Condense the final answer into a short, factual response.",
            context=answer_extraction
        )

        return final_answer