# Workflow ID: hotpotqa_161_0
# Benchmark: hotpotqa
# Data Indices: [294, 152]

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

        # Step 1: Initial Analysis - Classify question type and identify bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question and context documents:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract potential bridge entities that connect documents.
            3. List key documents relevant to the question.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Extract relevant information
        relevant_docs = await self.generate(
            instruction=f"""From the initial analysis:
            {initial_analysis}
            
            Identify all documents containing relevant information.
            Extract key facts, entities, and relationships from each document.
            Format as structured list.""",
            context=initial_analysis
        )
        doc_tasks = []
        for doc in relevant_docs.split('\n'):
            task = self.generate(
                instruction=f"""Analyze this document:
                {doc}
                
                Extract facts, entities, and relationships relevant to the question.
                Highlight potential bridge entities.""",
                context=initial_analysis
            )
            doc_tasks.append(task)
        doc_results = await asyncio.gather(*doc_tasks)

        # Step 3: Reasoning Chain Construction - Build connections between documents
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted information:
            Documents: {doc_results}
            
            Build a reasoning chain connecting the documents:
            1. Start with the question entity.
            2. Follow bridge entities to connect documents.
            3. End with the answer entity.
            Provide step-by-step reasoning.""",
            context=initial_analysis
        )

        # Step 4: Validation and Refinement - Validate the reasoning chain
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain:
            {reasoning_chain}
            
            Check for logical consistency and factual accuracy.
            Flag any missing or ambiguous information.""",
            context=initial_analysis
        )
        if "error" in validation.lower() or "missing" in validation.lower():
            refined_chain = await self.revise(
                instruction=f"""Revise the reasoning chain to address issues:
                {validation}
                
                Improve clarity, resolve ambiguities, and fill gaps.""",
                context=reasoning_chain
            )
            reasoning_chain = refined_chain

        # Step 5: Answer Extraction - Extract precise answer span
        answer = await self.generate(
            instruction=f"""Using the validated reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the final document.
            Ensure the answer is factually correct and concise.""",
            context=initial_analysis
        )

        return answer