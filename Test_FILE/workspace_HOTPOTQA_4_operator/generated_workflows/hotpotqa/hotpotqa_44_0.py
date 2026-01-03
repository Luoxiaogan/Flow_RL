# Workflow ID: hotpotqa_44_0
# Benchmark: hotpotqa
# Data Indices: [282, 21]

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

        # Initial Analysis: Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) and extract key entities:
            - Identify main entities mentioned in the question
            - Determine relationships between entities
            - Classify the type of reasoning required (e.g., bridge, comparison)""",
            context=""
        )

        # Parallel Document Exploration: Find relevant documents for each entity
        entities = [entity.strip() for entity in initial_analysis.split('\n') if entity.strip()]
        document_explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Find relevant documents and extract pertinent information for entity: {entity}
                - Identify document titles mentioning the entity
                - Extract sentences containing the entity and related facts""",
                context=""
            ) for entity in entities]
        )

        # Reasoning Chain Construction: Connect entities across documents
        refined_explorations = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine extracted information for entity: {entities[i]}
                - Ensure factual accuracy
                - Clarify ambiguous information
                - Connect with other entities if possible""",
                context=document_explorations[i]
            ) for i in range(len(entities))]
        )

        # Answer Synthesis: Combine insights and select the best answer
        synthesis = await self.ensemble(
            instruction="""Synthesize information from different documents to construct the reasoning chain:
            - Connect entities across documents
            - Derive the final answer based on the reasoning chain
            - Ensure answer is factually correct and supported by evidence""",
            contexts_list=refined_explorations
        )

        # Final Validation: Validate the reasoning chain and final answer
        final_validation = await self.generate(
            instruction=f"""Validate the constructed reasoning chain and final answer:
            - Check consistency across documents
            - Verify factual accuracy
            - Address any discrepancies or ambiguities""",
            context=synthesis
        )

        # Return the final validated answer
        return final_validation