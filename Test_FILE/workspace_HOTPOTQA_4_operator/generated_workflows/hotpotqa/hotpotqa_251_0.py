# Workflow ID: hotpotqa_251_0
# Benchmark: hotpotqa
# Data Indices: [150, 329]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities (people, places, numbers, actions).
            3. Highlight relationships between entities.
            Provide structured output:
            - Question Type: [type]
            - Key Entities: [list of entities]
            - Relationships: [list of relationships]""",
            context=""
        )

        # Step 2: Entity Linking - Find relevant documents and extract supporting facts
        entities = await self.generate(
            instruction=f"""Extract all key entities from the analysis:
            {analysis}
            
            For each entity, identify relevant documents and extract supporting facts.
            Format as:
            - Entity: [name]
              - Document Titles: [list of titles]
              - Supporting Facts: [list of sentences]""",
            context=analysis
        )

        # Step 3: Parallel Exploration - Build reasoning chains for each entity
        reasoning_tasks = []
        for entity in entities.split("\n- Entity: ")[1:]:
            task = self.generate(
                instruction=f"""For the entity:
                {entity}
                
                Build a reasoning chain by connecting documents through shared entities or relationships.
                Include:
                - Document Connections: [how documents are linked]
                - Supporting Evidence: [facts from each document]""",
                context=entities
            )
            reasoning_tasks.append(task)

        reasoning_chains = await asyncio.gather(*reasoning_tasks)

        # Step 4: Validation and Synthesis - Evaluate and merge reasoning chains
        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains:
            1. Assess factual correctness and completeness.
            2. Prioritize chains with clear evidence from multiple documents.
            3. Select the strongest chain.
            Provide the selected chain with supporting evidence.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Answer Extraction - Extract precise answer span
        answer = await self.generate(
            instruction=f"""From the reasoning chain:
            {best_chain}
            
            Extract the precise answer span directly from the text.
            Ensure the answer is factually correct and supported by evidence.
            Format as:
            - Answer: [exact span]
            - Supporting Facts: [list of sentences]""",
            context=best_chain
        )

        # Step 6: Iterative Refinement - Improve clarity and completeness
        refined_answer = await self.revise(
            instruction=f"""Refine the answer:
            - Ensure clarity and precision.
            - Add any missing details.
            - Validate against the original problem.
            Original Answer:
            {answer}""",
            context=answer
        )

        return refined_answer