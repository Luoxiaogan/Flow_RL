# Workflow ID: hotpotqa_159_0
# Benchmark: hotpotqa
# Data Indices: [130]

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

        # Step 1: Question Analysis
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type and extract key entities:
            - Is it a bridge question, comparison question, or compositional question?
            - What are the key entities mentioned in the question?
            - What is the expected answer format (short text span or yes/no)?
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Document Search
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        document_searches = []
        for doc in documents.split("Document ")[1:]:
            title, content = doc.split("\n", 1)
            document_searches.append(
                self.generate(
                    instruction=f"""Search this document for information related to the key entities:
                    Key Entities: {question_analysis}
                    Document Title: {title}
                    Document Content: {content}
                    Highlight relevant sentences and shared entities.""",
                    context=""
                )
            )
        search_results = await asyncio.gather(*document_searches)

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify shared entities or concepts across the search results:
            - What entities appear in multiple documents?
            - Which entities are most relevant to the question?
            Prioritize based on relevance and context.""",
            contexts_list=search_results
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain using the identified bridge entities:
            Bridge Entities: {bridge_entities}
            Search Results: {search_results}
            Trace connections between documents to arrive at the answer.""",
            context=""
        )

        # Step 5: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the reasoning chain for logical consistency and factual accuracy:
            Reasoning Chain: {reasoning_chain}
            Search Results: {search_results}
            Identify any inconsistencies or missing information.""",
            context=""
        )
        if "inconsistent" in validation.lower() or "missing" in validation.lower():
            reasoning_chain = await self.revise(
                instruction=f"""Refine the reasoning chain to address issues:
                Issues: {validation}
                Original Chain: {reasoning_chain}""",
                context=reasoning_chain
            )

        # Step 6: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer span or yes/no response from the final document:
            Reasoning Chain: {reasoning_chain}
            Expected Answer Format: {question_analysis}
            Ensure the output is factually correct and matches the expected format.""",
            context=""
        )

        return answer