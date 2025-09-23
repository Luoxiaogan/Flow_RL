# Workflow ID: hotpotqa_322_0
# Benchmark: hotpotqa
# Data Indices: [385]

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
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison, compositional).
            Identify key entities and relationships mentioned in the question.
            Provide structured output including:
            - Question Type: [bridge/comparison/compositional]
            - Key Entities: [list of entities]
            - Relationships: [how entities are related]""",
            context=""
        )

        # Step 2: Parallel Fact Extraction - Extract relevant facts from all documents
        documents = initial_analysis.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_titles = [line.split(":")[0].strip() for line in documents.split("\n") if line.startswith("Document")]
        fact_extraction_tasks = [
            self.generate(
                instruction=f"""Extract all facts related to the key entities from {doc_title}.
                Focus on information that could connect to other documents or answer the question.
                Format as structured list with categories:
                - Entities: [names and roles]
                - Properties: [attributes and values]
                - Relationships: [connections and interactions]""",
                context=initial_analysis
            ) for doc_title in doc_titles
        ]
        extracted_facts = await asyncio.gather(*fact_extraction_tasks)

        # Step 3: Reasoning Chain Construction - Build and validate the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted facts from all documents:
            {extracted_facts}
            
            Construct a reasoning chain that connects the key entities to answer the question.
            Ensure each step in the chain is supported by evidence from the documents.
            Format as a sequence of logical steps:
            - Step 1: [fact/evidence from Document X]
            - Step 2: [connection to Document Y]
            - Final Step: [answer derived from reasoning]""",
            context=initial_analysis
        )

        # Step 4: Answer Extraction and Validation - Extract precise answer and validate
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the final step of the reasoning chain:
                {reasoning_chain}
                
                Ensure the answer is a short text span or yes/no response directly supported by the documents.""",
                context=reasoning_chain
            ),
            self.revise(
                instruction=f"""Validate the reasoning chain and ensure factual correctness:
                {reasoning_chain}
                
                Identify any gaps or errors in the chain and suggest corrections.""",
                context=reasoning_chain
            )
        )
        final_answer = await self.ensemble(
            instruction="Select the most accurate and supported answer.",
            contexts_list=answer_candidates
        )

        return final_answer