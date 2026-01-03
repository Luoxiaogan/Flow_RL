# Workflow ID: hotpotqa_82_0
# Benchmark: hotpotqa
# Data Indices: [437, 197]

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

        # Step 1: Initial Analysis - Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem into one of the following types:
            1. Bridge: Requires connecting entities across documents.
            2. Comparison: Involves comparing properties across documents.
            3. Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Entity Extraction - Identify key entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the context documents:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Problem Classification: {classification}""",
            context=""
        )

        # Step 3: Reasoning Chain Construction - Build logical connections
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and problem classification:
            Entities: {entities}
            Classification: {classification}
            
            Construct a reasoning chain that connects the entities across documents to answer the question.
            Highlight the bridge entities and their relationships.""",
            context=entities
        )

        # Step 4: Parallel Exploration - Explore multiple reasoning paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Explore reasoning path 1:
                Start with {reasoning_chain.split('.')[0]}""",
                context=reasoning_chain
            ),
            self.generate(
                instruction=f"""Explore reasoning path 2:
                Start with {reasoning_chain.split('.')[1] if len(reasoning_chain.split('.')) > 1 else 'alternative perspective'}""",
                context=reasoning_chain
            )
        )

        # Step 5: Ensemble - Select or synthesize the best path
        best_path = await self.ensemble(
            instruction="""Evaluate the reasoning paths and select the most promising one.
            Criteria:
            - Completeness of connections
            - Clarity of reasoning
            - Relevance to the question""",
            contexts_list=paths
        )

        # Step 6: Answer Extraction - Extract precise answer
        answer = await self.generate(
            instruction=f"""Using the selected reasoning path:
            {best_path}
            
            Extract the precise answer from the final document in the chain.
            Ensure the answer is factually correct and directly addresses the question.""",
            context=best_path
        )

        # Step 7: Validation - Verify the answer against supporting facts
        validated_answer = await self.revise(
            instruction=f"""Verify the extracted answer:
            {answer}
            
            Cross-reference with the context documents to ensure factual accuracy.
            Correct any errors or ambiguities.""",
            context=answer
        )

        return validated_answer