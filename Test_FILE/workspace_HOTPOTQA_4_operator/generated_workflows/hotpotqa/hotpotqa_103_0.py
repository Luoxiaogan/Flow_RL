# Workflow ID: hotpotqa_103_0
# Benchmark: hotpotqa
# Data Indices: [32]

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

        # Step 1: Problem Analysis - Classify question type and extract key entities
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract all key entities (e.g., names, places, concepts).
            3. Identify potential bridge entities that connect documents.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Document Exploration - Extract relevant information from documents
        entities = await self.generate(
            instruction=f"""Given the analysis:
            {analysis}
            
            Extract relevant information from each document:
            - Focus on sentences containing key entities.
            - Highlight connections between entities across documents.
            - Identify supporting facts for each entity.""",
            context=analysis
        )

        # Parallelize document processing
        document_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            task = self.generate(
                instruction=f"""Process Document {i}:
                - Extract sentences related to key entities.
                - Identify bridge entities and their connections.
                - Summarize relevant facts.""",
                context=entities
            )
            document_tasks.append(task)
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Reasoning Chain Construction - Build logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information:
            {document_results}
            
            Construct a reasoning chain:
            - Connect bridge entities across documents.
            - Follow logical paths to answer the question.
            - Highlight supporting facts for each step.""",
            context="\n".join(document_results)
        )

        # Step 4: Answer Extraction - Extract precise answer span
        answer_extraction = await self.generate(
            instruction=f"""Extract the final answer:
            - Identify the exact text span that answers the question.
            - Ensure the answer is factually correct and supported by evidence.
            - Format the answer as a short phrase or yes/no response.""",
            context=reasoning_chain
        )

        # Step 5: Validation - Verify factual correctness
        validation = await self.revise(
            instruction=f"""Validate the extracted answer:
            - Cross-check with supporting facts from documents.
            - Ensure consistency with the reasoning chain.
            - Correct any errors or ambiguities.""",
            context=answer_extraction
        )

        # Step 6: Final Output - Return the validated answer
        final_answer = await self.summarize(
            instruction="Condense the validated answer into a concise response.",
            context=validation
        )

        return final_answer