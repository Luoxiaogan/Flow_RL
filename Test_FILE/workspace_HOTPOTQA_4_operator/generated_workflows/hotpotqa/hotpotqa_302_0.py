# Workflow ID: hotpotqa_302_0
# Benchmark: hotpotqa
# Data Indices: [59]

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

        # Step 1: Initial Analysis - Classify question type and identify key entities
        classification = await self.generate(
            instruction="""Analyze the question to determine its type and key elements:
            - Is it a bridge, comparison, or compositional question?
            - Identify the main entities or themes mentioned.
            - Highlight the expected answer format (e.g., short text span, yes/no).""",
            context=""
        )

        # Step 2: Parallel Extraction - Extract relevant sentences from all documents
        documents = [f"Document {i}" for i in range(1, 11)]  # Example: 10 documents
        extraction_tasks = [
            self.generate(
                instruction=f"""From {doc}, extract sentences relevant to the identified entities/themes:
                Focus on facts that could connect to other documents.
                Exclude irrelevant or redundant information.""",
                context=classification
            )
            for doc in documents
        ]
        extracted_sentences = await asyncio.gather(*extraction_tasks)

        # Step 3: Ensemble Analysis - Identify bridge entities and construct reasoning chains
        reasoning_chain = await self.ensemble(
            instruction="""Identify bridge entities that connect documents:
            - Find shared entities or themes across extracted sentences.
            - Construct potential reasoning chains linking these entities.
            - Evaluate which chain best supports answering the question.""",
            contexts_list=extracted_sentences
        )

        # Step 4: Validation and Refinement - Ensure factual accuracy and logical consistency
        refined_chain = await self.revise(
            instruction="""Validate the reasoning chain:
            - Check for factual accuracy against the original documents.
            - Ensure logical consistency across connections.
            - Refine the chain if ambiguities or conflicts are detected.""",
            context=reasoning_chain
        )

        # Step 5: Final Answer Extraction - Extract the precise answer span
        final_answer = await self.summarize(
            instruction="""Extract the exact answer span from the final document in the reasoning chain:
            - Ensure the answer is concise and directly supported by the text.
            - Format the answer according to the expected output (e.g., short text span, yes/no).""",
            context=refined_chain
        )

        return final_answer