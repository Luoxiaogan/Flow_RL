# Workflow ID: hotpotqa_333_0
# Benchmark: hotpotqa
# Data Indices: [489, 49]

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

        # Step 1: Analyze the question to classify type and extract entities
        question_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships.
            3. Identify the expected answer format (yes/no, short text).
            Provide structured output.""",
            context=""
        )

        # Step 2: Process documents in parallel to extract relevant information
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        document_tasks = []
        for doc in documents.split("Document ")[1:]:
            title, content = doc.split(":", 1)
            task = self.generate(
                instruction=f"""Extract sentences mentioning entities from {question_analysis}:
                - Focus on sentences with key entities.
                - Disambiguate entities based on context.
                - Highlight relationships between entities.""",
                context=content
            )
            document_tasks.append(task)
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Build reasoning chains across documents
        reasoning_chains = await self.generate(
            instruction=f"""Connect entities across documents:
            - Use shared attributes or relationships.
            - Build a step-by-step reasoning chain.
            - Ensure logical coherence.""",
            context="\n".join(document_results)
        )

        # Step 4: Extract and validate the final answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the final answer from the reasoning chain:
            - Ensure it matches the expected format from {question_analysis}.
            - Validate against supporting facts from {document_results}.
            Provide the final answer and supporting evidence.""",
            context=reasoning_chains
        )

        # Step 5: Refine and finalize the answer
        refined_answer = await self.revise(
            instruction="""Ensure clarity, precision, and factual accuracy:
            - Correct any ambiguities.
            - Add missing details if necessary.
            - Maintain short, factual format.""",
            context=answer_extraction
        )

        return refined_answer