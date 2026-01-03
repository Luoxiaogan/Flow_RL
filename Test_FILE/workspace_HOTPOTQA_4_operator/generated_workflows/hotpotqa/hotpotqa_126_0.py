# Workflow ID: hotpotqa_126_0
# Benchmark: hotpotqa
# Data Indices: [315]

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

        # Step 1: Extract entities and relationships from all documents
        initial_analysis = await asyncio.gather(
            *[self.generate(
                instruction="""Extract all named entities, relationships, and key facts:
                - Entities: Names, places, organizations
                - Relationships: Connections between entities
                - Facts: Specific details mentioned in the document""",
                context=""
            ) for _ in range(10)]  # Assuming 10 documents
        )

        # Step 2: Identify bridge entities across documents
        bridge_entities = await self.ensemble(
            instruction="""Identify shared entities and relationships across documents:
            - Find overlapping entities
            - Highlight connections between documents
            - Prioritize entities most relevant to the question""",
            contexts_list=initial_analysis
        )

        # Step 3: Construct reasoning chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the bridge entities: {bridge_entities}
                Construct a reasoning chain that connects documents:
                - Start with the question
                - Follow logical steps through shared entities
                - End with a potential answer""",
                context=doc_analysis
            ) for doc_analysis in initial_analysis]
        )

        # Step 4: Refine and extract precise answers
        refined_answers = await asyncio.gather(
            *[self.revise(
                instruction="""Refine the reasoning chain and extract the precise answer:
                - Ensure factual correctness
                - Extract exact answer spans or yes/no responses
                - Highlight supporting evidence""",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Synthesize final answer
        final_answer = await self.summarize(
            instruction="""Condense the reasoning chains into a concise, factual answer:
            - Preserve only essential information
            - Ensure clarity and precision
            - Include supporting evidence if necessary""",
            context="\n".join(refined_answers)
        )

        return final_answer