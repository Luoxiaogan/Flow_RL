# Workflow ID: hotpotqa_311_0
# Benchmark: hotpotqa
# Data Indices: [252]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Is it a bridge question (connecting entities across documents)?
            - A comparison question (comparing properties)?
            - A compositional question (combining multiple facts)?
            Provide reasoning for your classification.""",
            context=""
        )

        # Step 2: Parallel document analysis
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_sections = [doc.strip() for doc in documents.split("Document") if doc.strip()]
        parallel_results = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract key entities, dates, and relationships from this document: {doc}",
                context=""
            ) for doc in doc_sections]
        )

        # Step 3: Identify bridge entities (if applicable)
        if "bridge" in question_type.lower():
            bridge_entities = await self.generate(
                instruction=f"""Identify shared entities across documents:
                Documents: {parallel_results}
                Find overlapping entities that connect the reasoning chain.""",
                context=""
            )
            reasoning_chain = await self.generate(
                instruction=f"""Construct the reasoning chain using the bridge entities:
                Entities: {bridge_entities}
                Documents: {parallel_results}""",
                context=""
            )
        else:
            reasoning_chain = await self.generate(
                instruction=f"""Construct the reasoning chain without bridge entities:
                Documents: {parallel_results}""",
                context=""
            )

        # Step 4: Extract the answer
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the reasoning chain:
                Chain: {reasoning_chain}""",
                context=""
            ),
            self.revise(
                instruction="Refine the extracted answer for clarity and precision.",
                context=reasoning_chain
            )
        )

        # Step 5: Validate and finalize the answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and concise answer.",
            contexts_list=answer_candidates
        )

        return final_answer