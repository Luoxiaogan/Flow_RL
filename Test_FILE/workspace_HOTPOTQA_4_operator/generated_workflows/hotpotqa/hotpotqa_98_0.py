# Workflow ID: hotpotqa_98_0
# Benchmark: hotpotqa
# Data Indices: [8, 154]

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

        # Step 1: Initial Analysis and Classification
        classification = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question connecting documents through shared entities?
            2. Is it a comparison question contrasting properties across documents?
            3. Is it a compositional question combining multiple facts?
            Provide structured classification with reasoning.""",
            context=""
        )

        # Step 2: Parallel Document Analysis
        documents_analysis = await asyncio.gather(
            *[self.generate(
                instruction=f"""Analyze this document for relevant facts and entities:
                - Identify key entities and their relationships
                - Extract sentences that contain potential answers
                - Focus on information pertinent to the question type: {classification}""",
                context=""
            ) for _ in range(10)]  # Assuming up to 10 documents
        )

        # Step 3: Building Reasoning Chains
        reasoning_chain = await self.ensemble(
            instruction=f"""Evaluate and connect the following document analyses:
            Documents Analyses: {documents_analysis}
            
            Build a reasoning chain by:
            - Identifying shared entities or comparable properties
            - Establishing logical connections between facts
            - Prioritizing connections based on evidence strength and relevance to the question type: {classification}""",
            contexts_list=documents_analysis
        )

        # Step 4: Answer Extraction and Validation
        initial_answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            
            Ensure the answer is:
            - Factually correct based on the provided documents
            - A short text span or yes/no response
            - Directly supported by the reasoning chain""",
            context=reasoning_chain
        )

        validated_answer = await self.revise(
            instruction=f"""Critique and refine the extracted answer:
            Initial Answer: {initial_answer}
            
            Validate by:
            - Checking factual consistency with supporting facts
            - Ensuring precision and clarity
            - Highlighting any ambiguities or conflicts""",
            context=initial_answer
        )

        return validated_answer