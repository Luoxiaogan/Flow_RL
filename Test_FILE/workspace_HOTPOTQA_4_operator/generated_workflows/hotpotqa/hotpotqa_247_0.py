# Workflow ID: hotpotqa_247_0
# Benchmark: hotpotqa
# Data Indices: [50]

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
        import re

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the question and context documents:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities (people, organizations, events) mentioned in the question.
            3. List potential bridge entities that could connect documents.
            Provide structured output.""",
            context=""
        )

        # Parse entities and question type
        question_type = "bridge" if "bridge" in analysis.lower() else "comparison"
        entities = re.findall(r'\b[A-Z][a-zA-Z]+\b', analysis)  # Simplified entity extraction

        # Phase 2: Bridge Entity Identification
        if question_type == "bridge":
            entity_candidates = await asyncio.gather(
                *[self.generate(
                    instruction=f"Find mentions of {entity} in all documents and describe their roles.",
                    context=""
                ) for entity in entities]
            )
            bridge_entity = await self.ensemble(
                instruction="Select the most plausible bridge entity based on frequency and relevance.",
                contexts_list=entity_candidates
            )
        else:
            bridge_entity = None

        # Phase 3: Supporting Fact Extraction
        supporting_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"Extract sentences mentioning {bridge_entity or entity} from Document {i+1}.",
                context=""
            ) for i, entity in enumerate(entities)]
        )
        condensed_facts = await asyncio.gather(
            *[self.summarize(
                instruction="Condense extracted sentences into concise supporting facts.",
                context=fact
            ) for fact in supporting_facts]
        )

        # Phase 4: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Combine the following facts into a coherent reasoning chain:
            Facts: {condensed_facts}
            Ensure logical consistency and traceability.""",
            context=""
        )
        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity and factual accuracy.",
            context=reasoning_chain
        )

        # Phase 5: Final Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            Chain: {refined_chain}
            Ensure the answer matches the expected format (short text or yes/no).""",
            context=""
        )

        return answer