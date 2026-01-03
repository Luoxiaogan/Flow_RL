# Workflow ID: hotpotqa_120_0
# Benchmark: hotpotqa
# Data Indices: [392]

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

        # Step 1: Initial Analysis - Classify question and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract all named entities, numbers, and relationships.
            3. Identify constraints or conditions.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Identify relevant sentences and bridge entities
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip().split("Document")
        document_tasks = [
            self.generate(
                instruction=f"""Analyze this document:
                1. Extract sentences containing entities or concepts from the question.
                2. Identify potential bridge entities.
                3. Collect supporting facts.
                Document content: {doc}""",
                context=initial_analysis
            )
            for doc in documents if doc.strip()
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Build Reasoning Chains - Connect sentences through bridge entities
        reasoning_chain = await self.generate(
            instruction=f"""Using the following document analyses:
            {document_results}
            
            Build reasoning chains:
            1. Link sentences through shared entities or concepts.
            2. Ensure logical coherence.
            3. Resolve ambiguities or contradictions.""",
            context=initial_analysis
        )

        # Step 4: Validate and Refine - Ensure chain is sound and extract answer
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity and logical soundness.",
            context=reasoning_chain
        )

        # Step 5: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {refined_chain}
            
            Ensure the answer is supported by evidence from multiple documents.
            Provide the exact text span and supporting facts.""",
            context=initial_analysis
        )

        # Final Output
        return answer_extraction