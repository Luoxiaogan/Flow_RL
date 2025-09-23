# Workflow ID: hotpotqa_210_0
# Benchmark: hotpotqa
# Data Indices: [200, 263]

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

        # Stage 1: Question Analysis and Classification
        question_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge, comparison, or compositional question?
            2. Identify key entities and relationships mentioned in the question.
            3. Determine the expected answer format (short text span or yes/no).""",
            context=""
        )

        # Stage 2: Entity Extraction and Bridging
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract key entities and relationships from this document.",
                context=doc
            ) for doc in self.extract_documents()]
        )
        bridge_entities = await self.ensemble(
            instruction="Identify bridge entities that connect the documents.",
            contexts_list=document_summaries
        )

        # Stage 3: Reasoning Chain Construction
        intermediate_conclusions = []
        for i, summary in enumerate(document_summaries):
            conclusion = await self.generate(
                instruction=f"""Using the extracted entities and bridge entities:
                {bridge_entities}
                
                Construct an intermediate conclusion based on Document {i+1}.""",
                context=summary
            )
            refined_conclusion = await self.revise(
                instruction="Validate and refine the intermediate conclusion.",
                context=conclusion
            )
            intermediate_conclusions.append(refined_conclusion)

        reasoning_chain = "\n".join(intermediate_conclusions)

        # Stage 4: Answer Extraction and Finalization
        answer = await self.generate(
            instruction=f"""Based on the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the final document.""",
            context=""
        )

        return answer

    def extract_documents(self):
        # Helper function to extract document texts from the problem
        lines = self.problem_text.split("\n")
        documents = []
        current_doc = ""
        for line in lines:
            if line.startswith("Document"):
                if current_doc:
                    documents.append(current_doc.strip())
                current_doc = ""
            else:
                current_doc += line + "\n"
        if current_doc:
            documents.append(current_doc.strip())
        return documents