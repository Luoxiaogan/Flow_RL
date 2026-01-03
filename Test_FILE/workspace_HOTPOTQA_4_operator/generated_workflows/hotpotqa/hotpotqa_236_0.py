# Workflow ID: hotpotqa_236_0
# Benchmark: hotpotqa
# Data Indices: [45, 311]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities (people, places, organizations, etc.).
            3. Identify potential bridge entities that connect documents.
            Present findings in structured format.""",
            context=""
        )

        # Phase 2: Document Filtering
        relevant_docs = await self.generate(
            instruction=f"""Based on extracted entities:
            {analysis}
            
            Identify relevant documents by matching entities.
            List document titles and their relevance scores.""",
            context=analysis
        )

        # Phase 3: Parallel Reasoning Paths
        reasoning_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Build reasoning chain 1:
                Start with the first relevant document and follow connections.""",
                context=relevant_docs
            ),
            self.generate(
                instruction=f"""Build reasoning chain 2:
                Start with the second relevant document and follow connections.""",
                context=relevant_docs
            )
        )

        # Phase 4: Ensemble to Select Best Path
        selected_path = await self.ensemble(
            instruction="""Compare reasoning paths:
            1. Evaluate completeness of chains.
            2. Check factual consistency.
            3. Select the most supported path.""",
            contexts_list=reasoning_paths
        )

        # Phase 5: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the final document:
            Selected reasoning path:
            {selected_path}
            
            Ensure exact phrasing matches the document text.""",
            context=selected_path
        )

        # Phase 6: Validation and Refinement
        validated_answer = await self.revise(
            instruction=f"""Validate the answer:
            1. Verify factual correctness.
            2. Ensure supporting facts are cited.
            3. Refine phrasing if needed.""",
            context=answer
        )

        return validated_answer