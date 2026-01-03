# Workflow ID: hotpotqa_28_0
# Benchmark: hotpotqa
# Data Indices: [461]

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
            instruction="""Classify the question into one of the following types:
            - Bridge: Requires connecting shared entities across documents.
            - Comparison: Involves comparing properties from different documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )
        
        # Step 2: Extract entities and relationships from all documents
        entity_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from Document {i+1}:
                - Entities: [names, places, organizations]
                - Relationships: [how entities are connected]""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        entities_list = await asyncio.gather(*entity_tasks)
        entities_summary = "\n".join(entities_list)
        
        # Step 3: Build reasoning chains based on question type
        if "bridge" in question_type.lower():
            reasoning_chains = await self.generate(
                instruction=f"""Identify shared entities across documents:
                Entities Summary: {entities_summary}
                Find entities that connect multiple documents and explain their relationships.""",
                context=entities_summary
            )
        elif "comparison" in question_type.lower():
            reasoning_chains = await self.generate(
                instruction=f"""Compare properties across documents:
                Entities Summary: {entities_summary}
                Identify relevant properties and evaluate their differences.""",
                context=entities_summary
            )
        else:  # Compositional
            reasoning_chains = await self.generate(
                instruction=f"""Combine multiple facts to derive the answer:
                Entities Summary: {entities_summary}
                Explain how different facts contribute to the final answer.""",
                context=entities_summary
            )
        
        # Step 4: Ensemble to select the best reasoning chain
        reasoning_options = reasoning_chains.split("\n\n")  # Split into individual chains
        best_chain = await self.ensemble(
            instruction="Select the most plausible reasoning chain based on coherence and factual support.",
            contexts_list=reasoning_options
        )
        
        # Step 5: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {best_chain}
            Ensure the answer is factually correct and directly supported by the text.""",
            context=best_chain
        )
        validated_answer = await self.revise(
            instruction="Validate and refine the answer for accuracy and clarity.",
            context=answer
        )
        
        return validated_answer