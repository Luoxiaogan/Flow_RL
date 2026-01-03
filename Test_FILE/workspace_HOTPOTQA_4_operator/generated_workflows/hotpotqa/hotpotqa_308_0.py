# Workflow ID: hotpotqa_308_0
# Benchmark: hotpotqa
# Data Indices: [356, 251]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities and relationships mentioned in the question.
            3. Provide a structured summary of the findings.""",
            context=""
        )

        # Step 2: Parallel Entity and Relationship Extraction
        # Extract entities and relationships from each document
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("\n\n")
        extraction_tasks = [
            self.generate(
                instruction=f"""Extract all entities and relationships from the following document:
                {doc}
                Format as a structured list with categories:
                - Entities: [names and roles]
                - Relationships: [connections and interactions]""",
                context=""
            ) for doc in documents if doc.strip()
        ]
        extracted_data = await asyncio.gather(*extraction_tasks)

        # Merge extracted data into a unified view
        unified_view = await self.ensemble(
            instruction="Combine all extracted entities and relationships into a unified view.",
            contexts_list=extracted_data
        )

        # Step 3: Reasoning Chain Construction (Conditional Branching)
        if "bridge" in initial_analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for a bridge question:
                Unified View: {unified_view}
                Identify shared entities and follow connections between documents to answer the question.""",
                context=initial_analysis
            )
        elif "comparison" in initial_analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for a comparison question:
                Unified View: {unified_view}
                Extract and compare properties across documents to answer the question.""",
                context=initial_analysis
            )
        else:
            reasoning_chain = await self.generate(
                instruction=f"""Construct a reasoning chain for a compositional question:
                Unified View: {unified_view}
                Combine multiple facts to derive the answer.""",
                context=initial_analysis
            )

        # Step 4: Answer Extraction and Validation (Iterative Loop)
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short text span or yes/no response.""",
            context=""
        )

        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the answer:
                Answer: {answer}
                Check if it is factually correct and supported by the documents.""",
                context=reasoning_chain
            )
            if "correct" in validation.lower():
                break
            answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                Feedback: {validation}""",
                context=answer
            )

        return answer