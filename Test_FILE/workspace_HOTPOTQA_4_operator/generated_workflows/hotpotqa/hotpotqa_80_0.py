# Workflow ID: hotpotqa_80_0
# Benchmark: hotpotqa
# Data Indices: [441, 321]

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

        # Step 1: Initial Analysis - Classify question type and extract bridge entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question and context documents:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify potential bridge entities connecting documents.
            3. Extract key facts related to these entities from each document.
            Provide structured output with clear classifications and entities.""",
            context=""
        )

        # Step 2: Parallel Document Analysis - Extract detailed facts
        documents = [f"Document {i+1}" for i in range(10)]  # Assuming up to 10 documents
        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"""From {doc}, extract all facts related to entities identified in the initial analysis.
                Focus on information that connects to other documents.""",
                context=initial_analysis
            ) for doc in documents]
        )

        # Step 3: Ensemble - Merge facts and identify strongest reasoning chain
        reasoning_chain = await self.ensemble(
            instruction="""Merge facts from all documents:
            1. Identify the strongest connections between entities.
            2. Construct a reasoning chain that answers the question.
            3. Validate the chain against the question and context documents.""",
            contexts_list=document_facts
        )

        # Step 4: Refinement - Strengthen reasoning chain and validate facts
        refined_chain = await self.revise(
            instruction="""Refine the reasoning chain:
            1. Ensure all facts are supported by the context documents.
            2. Resolve any ambiguities or conflicts.
            3. Highlight the exact answer span or yes/no response.""",
            context=reasoning_chain
        )

        # Step 5: Summarization - Condense reasoning chain into concise output
        final_answer = await self.summarize(
            instruction="""Summarize the reasoning chain:
            1. Extract the exact answer span or yes/no response.
            2. Provide a brief explanation of the reasoning process.
            Ensure the output is concise and directly addresses the question.""",
            context=refined_chain
        )

        return final_answer