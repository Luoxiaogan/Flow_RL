# Workflow ID: hotpotqa_107_0
# Benchmark: hotpotqa
# Data Indices: [393]

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
        import re

        # Step 1: Question Classification and Document Analysis
        classification = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge, comparison, or compositional question?
            2. Identify key entities and relationships in the question.
            3. List all documents mentioning these entities.
            Provide structured output with classifications and document relevance.""",
            context=""
        )

        # Extract relevant documents dynamically
        relevant_docs = re.findall(r"Document \d+", classification)

        # Step 2: Parallel Document Analysis
        async def analyze_document(doc):
            return await self.generate(
                instruction=f"""Analyze {doc}:
                - Identify key sentences containing bridge entities.
                - Extract relevant facts about these entities.
                Provide structured output with extracted facts.""",
                context=classification
            )
        
        document_analyses = await asyncio.gather(
            *[analyze_document(doc) for doc in relevant_docs]
        )

        # Step 3: Building Reasoning Chains
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from analyzed documents:
            - Identify logical connections between facts.
            - Build a reasoning chain to answer the question.
            Provide a coherent chain of reasoning.""",
            contexts_list=document_analyses
        )

        # Step 4: Answer Extraction and Validation
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            
            Ensure the answer is:
            - Factually correct.
            - Directly supported by the text.
            - In the required format (short text span or yes/no).""",
            context=reasoning_chain
        )

        refined_answer = await self.revise(
            instruction="""Validate and refine the extracted answer:
            - Verify factual accuracy.
            - Ensure logical consistency.
            - Improve clarity if needed.""",
            context=answer
        )

        return refined_answer