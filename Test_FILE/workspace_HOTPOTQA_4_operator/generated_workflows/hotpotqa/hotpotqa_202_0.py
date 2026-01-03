# Workflow ID: hotpotqa_202_0
# Benchmark: hotpotqa
# Data Indices: [237]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Bridge: Requires connecting documents through shared entities.
            - Comparison: Requires comparing properties across documents.
            - Compositional: Requires combining multiple facts sequentially.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        entities_tasks = [
            self.generate(
                instruction=f"""Extract named entities, relationships, and key facts from this document:
                {doc}
                Format as structured list with categories:
                - Entities: [names, roles, organizations]
                - Relationships: [connections between entities]
                - Key Facts: [important statements or data points]""",
                context=""
            ) for doc in ["Document 1", "Document 2", "Document 3"]  # Dynamically populate with actual document titles
        ]
        entities_results = await asyncio.gather(*entities_tasks)

        # Step 3: Build the reasoning chain based on question type
        if "bridge" in question_type.lower():
            bridge_entity = await self.generate(
                instruction=f"""Identify the shared entity that connects the following documents:
                Entities from Document 1: {entities_results[0]}
                Entities from Document 2: {entities_results[1]}
                Entities from Document 3: {entities_results[2]}
                Provide the entity and explain how it connects the documents.""",
                context=question_type
            )
            reasoning_chain = await self.generate(
                instruction=f"""Using the bridge entity: {bridge_entity}
                Construct a reasoning chain that connects the documents and leads to the answer.
                Ensure each step is logically consistent and supported by evidence.""",
                context="\n".join(entities_results)
            )
        elif "comparison" in question_type.lower():
            comparison_results = await asyncio.gather(
                self.generate(instruction="Extract properties for comparison from Document 1...", context=entities_results[0]),
                self.generate(instruction="Extract properties for comparison from Document 2...", context=entities_results[1])
            )
            reasoning_chain = await self.generate(
                instruction=f"""Compare the following properties:
                Properties from Document 1: {comparison_results[0]}
                Properties from Document 2: {comparison_results[1]}
                Determine which property satisfies the question and explain the reasoning.""",
                context="\n".join(comparison_results)
            )
        else:  # Compositional
            reasoning_steps = []
            for i, entities in enumerate(entities_results):
                step = await self.generate(
                    instruction=f"""Using entities from Document {i+1}: {entities}
                    Identify the next fact needed to progress toward the answer.
                    Ensure the fact is logically connected to the previous step.""",
                    context="\n".join(reasoning_steps)
                )
                reasoning_steps.append(step)
            reasoning_chain = "\n".join(reasoning_steps)

        # Step 4: Refine the reasoning chain
        refined_chain = await self.revise(
            instruction="""Review the reasoning chain for logical consistency and completeness:
            - Are all steps clearly connected?
            - Is there sufficient evidence for each step?
            - Does the chain lead to the final answer?""",
            context=reasoning_chain
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Using the refined reasoning chain: {refined_chain}
            Extract the precise answer to the question.
            Ensure the answer is factually correct and directly supported by the documents.""",
            context=refined_chain
        )

        # Step 6: Summarize supporting facts
        supporting_facts = await self.summarize(
            instruction="""Condense the supporting facts from the reasoning chain:
            - Include only the most relevant facts.
            - Maintain logical flow and clarity.""",
            context=refined_chain
        )

        return {
            "answer": answer,
            "supporting_facts": supporting_facts
        }