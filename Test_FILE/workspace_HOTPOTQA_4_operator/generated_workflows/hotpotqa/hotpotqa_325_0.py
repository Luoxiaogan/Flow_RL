# Workflow ID: hotpotqa_325_0
# Benchmark: hotpotqa
# Data Indices: [447]

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
        analysis = await self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Identify key entities or concepts in the question.
            3. What is the expected answer format?""",
            context=""
        )

        # Step 2: Document Analysis (Parallel)
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        doc_titles = [line.split(":")[0].strip() for line in documents.split("\n") if line.startswith("Document")]
        doc_contents = [line.split(":")[1].strip() for line in documents.split("\n") if line.startswith("Document")]

        async def analyze_document(title, content):
            return await self.generate(
                instruction=f"""Analyze the document titled "{title}":
                1. Extract key entities and relationships.
                2. Identify facts relevant to the question.
                3. Highlight potential bridge entities.""",
                context=content
            )

        doc_analyses = await asyncio.gather(
            *[analyze_document(title, content) for title, content in zip(doc_titles, doc_contents)]
        )

        # Step 3: Bridge Entity Identification
        bridge_entities = await self.ensemble(
            instruction="""Identify shared entities or concepts that connect documents:
            1. Evaluate each document's analysis for overlapping entities.
            2. Select the most plausible bridge entity based on relevance to the question.""",
            contexts_list=doc_analyses
        )

        # Step 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the identified bridge entities: {bridge_entities}
            Construct a reasoning chain that connects the question to the answer:
            1. Start with the question and identify the first relevant fact.
            2. Follow the chain of facts across documents.
            3. End with the final fact that directly answers the question.""",
            context="\n".join(doc_analyses)
        )

        # Step 5: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the final document in the reasoning chain:
            1. Identify the exact text span or yes/no response.
            2. Ensure the answer is factually correct and supported by the evidence chain.""",
            context=reasoning_chain
        )

        # Step 6: Validation and Summary
        validation = await self.revise(
            instruction="""Validate the reasoning chain and answer:
            1. Check logical consistency.
            2. Verify factual correctness.
            3. Ensure the answer matches the expected format.""",
            context=answer
        )

        evidence_summary = await self.summarize(
            instruction="""Summarize the evidence chain:
            1. List supporting facts from each document.
            2. Highlight how they connect to form the reasoning chain.""",
            context=reasoning_chain
        )

        return {
            "answer": validation,
            "evidence_summary": evidence_summary
        }