# Workflow ID: hotpotqa_7_0
# Benchmark: hotpotqa
# Data Indices: [189, 187]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to:
            1. Classify it as a bridge or comparison question.
            2. Extract key entities and relationships.
            3. Identify potential bridge entities.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Entity Search - Find entities in all documents
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        searches = [
            self.generate(
                instruction=f"""Search for the following entities in this document:
                {initial_analysis}
                Document text: {doc}""",
                context=""
            ) for doc in documents
        ]
        search_results = await asyncio.gather(*searches)

        # Step 3: Summarize Search Results - Identify bridge entities
        summary = await self.summarize(
            instruction="Summarize entity matches across documents and identify bridge entities.",
            context="\n".join(search_results)
        )

        # Step 4: Reasoning Chain Construction - Link documents through bridge entities
        reasoning_chain = await self.ensemble(
            instruction="Construct a reasoning chain by linking documents through identified bridge entities.",
            contexts_list=search_results
        )

        # Step 5: Answer Extraction - Extract and validate the final answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            {reasoning_chain}
            Ensure the answer is factually correct and matches the question.""",
            context=""
        )

        # Step 6: Iterative Refinement - Improve answer if necessary
        refined_answer = await self.revise(
            instruction="Validate and refine the answer for clarity, correctness, and precision.",
            context=answer
        )

        return refined_answer