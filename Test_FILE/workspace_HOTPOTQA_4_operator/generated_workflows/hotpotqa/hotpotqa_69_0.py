# Workflow ID: hotpotqa_69_0
# Benchmark: hotpotqa
# Data Indices: [70, 298]

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

        # Initial Analysis: Classify question type and extract key components
        classification = await self.generate(
            instruction="""Classify the question type and identify key components:
            - Is it a bridge, comparison, or compositional question?
            - What are the main entities or properties involved?
            - What is the expected answer format?""",
            context=""
        )

        # Entity and Fact Extraction: Extract entities and facts from each document
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, relationships, and key facts from the following document:
                {doc}""",
                context=""
            ) for doc in documents
        ]
        extracted_info = await asyncio.gather(*extraction_tasks)

        # Merge extracted information into a unified context
        merged_context = await self.ensemble(
            instruction="Merge extracted entities and facts into a unified context",
            contexts_list=extracted_info
        )

        # Reasoning Chain Construction: Build reasoning chains by connecting entities and facts
        reasoning_chain = await self.generate(
            instruction=f"""Using the merged context:
            {merged_context}
            
            Construct a reasoning chain that connects the entities and facts to answer the question:
            {classification}""",
            context=merged_context
        )

        # Validate reasoning chain for logical consistency
        validated_chain = await self.revise(
            instruction="Critique and correct the reasoning chain for logical consistency",
            context=reasoning_chain
        )

        # Answer Extraction and Validation: Extract precise answer from the final document
        answer = await self.generate(
            instruction=f"""Using the validated reasoning chain:
            {validated_chain}
            
            Extract the precise answer from the relevant document and validate it against the supporting facts""",
            context=validated_chain
        )

        return answer