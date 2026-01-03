# Workflow ID: hotpotqa_96_0
# Benchmark: hotpotqa
# Data Indices: [491]

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

        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Bridge Question: Connects entities across documents (e.g., "What nationality is the director of [movie]?")
            - Comparison Question: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional Question: Combines multiple facts to derive an answer
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_tasks = [
            self.generate(
                instruction=f"""Extract named entities, relationships, and constraints from the following document:
                {doc}
                Format as structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )
            for doc in ["Document 1", "Document 2", "Document 3"]  # Dynamically adjust based on input
        ]
        entities_results = await asyncio.gather(*entities_tasks)

        # Combine extracted entities into a single context
        combined_entities = "\n".join(entities_results)

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {combined_entities}
            
            Construct a reasoning chain that connects the information across documents to answer the question:
            {classification}
            Ensure the chain includes supporting facts from at least two documents.""",
            context=combined_entities
        )

        # Validate and refine the reasoning chain
        refined_chain = await self.revise(
            instruction="""Validate the reasoning chain:
            - Are the connections between entities logical?
            - Are the supporting facts factually correct?
            - Does the chain lead to the final answer?
            If any issues are found, refine the chain accordingly.""",
            context=reasoning_chain
        )

        # Step 4: Extract and validate the answer
        answer = await self.summarize(
            instruction=f"""Using the refined reasoning chain:
            {refined_chain}
            
            Extract the precise answer to the question. The answer should be:
            - A short text span (entity/phrase) or yes/no response
            - Directly supported by the reasoning chain""",
            context=refined_chain
        )

        # Final validation
        final_answer = await self.revise(
            instruction="""Ensure the answer is factually correct and directly addresses the question:
            - Verify against the original documents
            - Confirm precision and clarity
            If necessary, make adjustments.""",
            context=answer
        )

        return final_answer