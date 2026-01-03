# Workflow ID: hotpotqa_178_0
# Benchmark: hotpotqa
# Data Indices: [208]

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

        # Step 1: Question Analysis
        analysis = await self.generate(
            instruction="""Classify the question type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities (people, places, organizations).
            - Highlight relationships between entities.
            Provide a structured classification.""",
            context=""
        )

        # Step 2: Document Filtering
        filtered_docs = await self.generate(
            instruction=f"""Filter documents based on key entities:
            Entities: {re.findall(r'\b[A-Z][a-zA-Z]*\b', analysis)}
            - Identify documents containing these entities.
            - Rank documents by relevance to the question.
            Return a ranked list of relevant documents.""",
            context=analysis
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct reasoning chain for document pair:
                Documents: {doc_pair}
                - Find shared entities or connecting facts.
                - Trace the reasoning chain across documents.
                - Ensure logical coherence.""",
                context=filtered_docs
            ) for doc_pair in re.findall(r'Document \d+:.*?(?=Document|\Z)', filtered_docs, re.DOTALL)]
        )

        # Step 4: Answer Extraction and Validation
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract precise answer from reasoning chain:
                Chain: {chain}
                - Identify the exact answer span.
                - Validate against supporting facts.""",
                context=chain
            ) for chain in reasoning_chains]
        )

        best_answer = await self.ensemble(
            instruction="Select the most accurate and supported answer.",
            contexts_list=candidate_answers
        )

        # Step 5: Output Formatting
        formatted_output = await self.generate(
            instruction=f"""Format the final output:
            Answer: {best_answer}
            - Provide a short, factual answer.
            - List supporting facts with document references.""",
            context=best_answer
        )

        return formatted_output