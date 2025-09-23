# Workflow ID: hotpotqa_53_0
# Benchmark: hotpotqa
# Data Indices: [186, 125]

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

        # Step 1: Analyze the problem to classify its type and extract key entities
        problem_analysis = await self.generate(
            instruction="""Analyze the problem to:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify the main subject and target property.
            3. Extract potential bridge entities that connect documents.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Explore documents in parallel to locate relevant information
        documents = await self.generate(
            instruction="Extract all document titles and their content.",
            context=""
        )
        exploration_tasks = [
            self.generate(
                instruction=f"""Search for sentences in '{doc}' that contain:
                1. The main subject: {problem_analysis.split('Main Subject:')[1].split('Target Property:')[0].strip()}
                2. Potential bridge entities: {problem_analysis.split('Bridge Entities:')[1].strip()}
                Return relevant sentences.""",
                context=doc
            ) for doc in documents.split("\n\n")
        ]
        relevant_sentences = await asyncio.gather(*exploration_tasks)

        # Step 3: Construct the reasoning chain using ensemble
        reasoning_chain = await self.ensemble(
            instruction="""Evaluate candidate connections between documents:
            1. Ensure factual consistency.
            2. Prioritize logical coherence.
            3. Select the most plausible reasoning path.""",
            contexts_list=relevant_sentences
        )

        # Step 4: Extract and validate the precise answer
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {reasoning_chain}
            Extract the precise answer as a short text span or yes/no response.
            Validate the answer against the original documents.""",
            context=reasoning_chain
        )

        # Final result
        return answer_extraction