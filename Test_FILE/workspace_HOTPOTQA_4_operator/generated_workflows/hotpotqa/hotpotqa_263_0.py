# Workflow ID: hotpotqa_263_0
# Benchmark: hotpotqa
# Data Indices: [69]

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

        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities that might connect documents.
            3. List potential bridge entities and their roles.
            Provide structured output.""",
            context=""
        )

        # Extract entities and prepare for parallel exploration
        entities = await self.generate(
            instruction=f"""From the analysis:
            {analysis}
            
            Extract all potential bridge entities and their descriptions.
            Format as a list: [entity1, entity2, ...]""",
            context=analysis
        )
        entities_list = entities.split(", ")

        # Phase 2: Parallel Entity Exploration
        entity_explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Explore the presence and significance of '{entity}' across documents.
                - Which documents mention this entity?
                - What role does it play in each document?
                - How might it connect to other entities?""",
                context=""
            ) for entity in entities_list]
        )

        # Phase 3: Build and Validate Reasoning Chains
        reasoning_chains = await self.ensemble(
            instruction="""Synthesize the entity explorations into reasoning chains:
            - Connect entities across documents logically.
            - Ensure each chain leads toward answering the question.
            - Prioritize chains with stronger document support.""",
            contexts_list=entity_explorations
        )

        validated_chains = await self.revise(
            instruction="""Critique and refine the reasoning chains:
            - Check for logical consistency.
            - Eliminate weak or unsupported chains.
            - Suggest improvements if needed.""",
            context=reasoning_chains
        )

        # Phase 4: Extract and Ensemble Candidate Answers
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""From the reasoning chain:
                {chain}
                
                Extract the precise answer span from the final document.
                Ensure the answer is factual and directly supported by the text.""",
                context=""
            ) for chain in validated_chains.split("\n\n")]
        )

        final_answer = await self.ensemble(
            instruction="""Select the best answer from the candidates:
            - Ensure factual correctness.
            - Align with the question requirements.
            - Trace back to supporting facts in the documents.""",
            contexts_list=candidate_answers
        )

        # Phase 5: Refine and Summarize
        refined_answer = await self.revise(
            instruction="""Improve clarity and precision of the final answer:
            - Ensure it is concise and directly addresses the question.
            - Add any missing details if necessary.""",
            context=final_answer
        )

        summary = await self.summarize(
            instruction="""Condense the reasoning chain and supporting facts:
            - Highlight key connections between entities.
            - Summarize how the answer was derived.""",
            context=refined_answer
        )

        return {
            "answer": refined_answer,
            "summary": summary
        }