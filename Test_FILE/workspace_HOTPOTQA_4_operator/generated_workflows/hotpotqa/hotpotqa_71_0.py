# Workflow ID: hotpotqa_71_0
# Benchmark: hotpotqa
# Data Indices: [469]

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

        # Step 1: Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the question type (bridge, comparison, compositional).
            - Extract key entities and relationships.
            - Identify the expected answer format.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Document Analysis
        documents = re.findall(r"Document \d+:.*?(?=\n\n|$)", self.problem_text, re.DOTALL)
        document_summaries = await asyncio.gather(
            *[self.generate(
                instruction=f"Summarize key facts from this document related to {problem_analysis}",
                context=doc
            ) for doc in documents]
        )

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify shared entities or concepts across documents:
            - Find overlapping entities or relationships.
            - Prioritize entities relevant to the question type.
            Provide a concise list of bridge entities.""",
            contexts_list=document_summaries
        )

        # Step 4: Conditional Branching
        if "bridge" in problem_analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Follow the reasoning chain starting from these bridge entities: {bridge_entities}
                - Connect documents through shared entities.
                - Derive the final answer step-by-step.
                Provide the answer and supporting facts.""",
                context=""
            )
        elif "comparison" in problem_analysis.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Compare properties across documents based on these bridge entities: {bridge_entities}
                - Identify differences or similarities.
                - Determine the correct answer.
                Provide the answer and supporting facts.""",
                context=""
            )
        else:  # Compositional or other types
            reasoning_chain = await self.generate(
                instruction=f"""Combine multiple facts from these bridge entities: {bridge_entities}
                - Synthesize information to derive the answer.
                Provide the answer and supporting facts.""",
                context=""
            )

        # Step 5: Answer Extraction and Validation
        raw_answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain: {reasoning_chain}
            - Ensure the answer is verbatim from the text.
            - Validate against supporting facts.
            Provide the final answer.""",
            context=""
        )

        refined_answer = await self.revise(
            instruction="Refine the answer for clarity and precision.",
            context=raw_answer
        )

        return refined_answer