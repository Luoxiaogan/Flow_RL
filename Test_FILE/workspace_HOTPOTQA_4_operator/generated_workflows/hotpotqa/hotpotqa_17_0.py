# Workflow ID: hotpotqa_17_0
# Benchmark: hotpotqa
# Data Indices: [108, 244]

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

        # Step 1: Problem Decomposition and Classification
        classification = await self.generate(
            instruction="""Analyze the problem and classify the question type:
            - Is it a bridge question, comparison question, or compositional question?
            - Extract key entities mentioned in the question.
            - Identify relevant documents based on these entities.
            Provide structured output with clear reasoning.""",
            context=""
        )

        # Step 2: Entity Extraction and Document Linking
        entities_extraction_tasks = [
            self.generate(
                instruction=f"""Extract entities and relationships from the following document:
                {doc}
                Focus on entities related to the question and identify connections between them.""",
                context=classification
            )
            for doc in self.extract_documents()  # Helper function to extract document texts
        ]
        entities_results = await asyncio.gather(*entities_extraction_tasks)

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain based on the extracted entities and connections:
            {classification}
            Entities and Connections:
            {' '.join(entities_results)}
            Follow the logical flow from the question to the final answer, ensuring each step is supported by evidence.""",
            context=""
        )

        # Step 4: Answer Extraction and Validation
        answer = await self.summarize(
            instruction="""Extract the precise answer from the reasoning chain:
            - Ensure the answer is a short text span or a yes/no response.
            - Verify that the answer is factually correct based on the supporting facts.""",
            context=reasoning_chain
        )

        # Handle edge cases with ensemble
        if "multiple options" in reasoning_chain.lower():
            options = await asyncio.gather(
                self.generate(instruction="Generate alternative answer 1...", context=reasoning_chain),
                self.generate(instruction="Generate alternative answer 2...", context=reasoning_chain)
            )
            answer = await self.ensemble(
                instruction="Select the most plausible answer based on supporting evidence.",
                contexts_list=options
            )

        return answer

    def extract_documents(self):
        # Helper function to extract document texts from the problem
        # Implementation depends on the specific input format
        pass