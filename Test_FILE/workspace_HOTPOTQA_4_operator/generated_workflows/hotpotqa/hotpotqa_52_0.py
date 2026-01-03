# Workflow ID: hotpotqa_52_0
# Benchmark: hotpotqa
# Data Indices: [161, 361]

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

        # Step 1: Analyze the question to identify type and extract entities
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type and extract key components:
            - Identify if it's a bridge, comparison, or compositional question
            - Extract named entities, relationships, and constraints
            - Highlight any ambiguities or missing information
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Identify bridge entities and link documents (parallel processing)
        documents = self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].strip()
        document_titles = [line.split(":")[0].strip() for line in documents.split("\n") if line.startswith("Document")]
        bridge_tasks = [
            self.generate(
                instruction=f"""Analyze the content of '{title}' to find connections with the extracted entities:
                - Highlight shared entities or concepts
                - Identify relevant sentences or facts
                Provide concise output.""",
                context=question_analysis
            ) for title in document_titles
        ]
        bridge_results = await asyncio.gather(*bridge_tasks)

        # Step 3: Ensemble to determine the most relevant bridge entities
        bridge_entities = await self.ensemble(
            instruction="""Synthesize the results to identify the most relevant bridge entities:
            - Prioritize entities with strong connections across multiple documents
            - Resolve conflicts or ambiguities
            Provide a ranked list of bridge entities.""",
            contexts_list=bridge_results
        )

        # Step 4: Construct the reasoning chain (iterative refinement)
        reasoning_chain = ""
        for entity in bridge_entities.split("\n"):
            if not entity.strip():
                continue
            chain_step = await self.generate(
                instruction=f"""Using the bridge entity '{entity}', construct the next step in the reasoning chain:
                - Trace connections to other documents
                - Extract supporting facts
                - Build towards the final answer
                Provide detailed output.""",
                context=reasoning_chain
            )
            reasoning_chain += chain_step + "\n"

        # Step 5: Extract and validate the answer
        answer = await self.summarize(
            instruction="""Extract the precise answer from the reasoning chain:
            - Focus on short text spans or yes/no responses
            - Ensure factual correctness
            Provide the final answer.""",
            context=reasoning_chain
        )

        validation = await self.revise(
            instruction=f"""Validate the extracted answer against the original documents and reasoning chain:
            - Check for factual consistency
            - Highlight any discrepancies
            - Suggest corrections if needed
            Provide the validated answer.""",
            context=answer
        )

        return validation