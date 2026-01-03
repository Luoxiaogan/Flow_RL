# Workflow ID: hotpotqa_14_0
# Benchmark: hotpotqa
# Data Indices: [374]

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

        # Step 1: Initial Analysis - Classify problem and extract entities
        initial_analysis = await self.generate(
            instruction="""Classify the problem type:
            - Is it a bridge question, comparison question, or compositional?
            - Extract all named entities (people, places, organizations) from the question and documents.
            - Identify potential bridge entities that appear in multiple documents.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Identify relevant sentences per document
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_tasks = []
        for doc in documents[1:]:
            title, content = doc.split(":", 1)
            task = self.generate(
                instruction=f"""From this document titled '{title.strip()}':
                - Identify sentences containing bridge entities.
                - Highlight connections between entities and the question.
                Provide concise output.""",
                context=initial_analysis
            )
            document_tasks.append(task)
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Merge Connections - Build unified reasoning chains
        merged_connections = await self.ensemble(
            instruction="""Merge the findings from all documents:
            - Identify shared entities and their roles.
            - Construct reasoning chains that connect the question to potential answers.
            - Select the most plausible chain based on evidence.""",
            contexts_list=document_results
        )

        # Step 4: Answer Extraction - Derive precise answer
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {merged_connections}
            
            Extract the precise answer to the question:
            - Ensure it is factually correct and directly supported by the documents.
            - Format the answer as a short text span or yes/no response.""",
            context=merged_connections
        )

        # Step 5: Refinement - Improve clarity and precision
        refined_answer = await self.revise(
            instruction="""Refine the extracted answer:
            - Verify factual accuracy.
            - Ensure precision and conciseness.
            - Match the expected answer format.""",
            context=answer_extraction
        )

        return refined_answer