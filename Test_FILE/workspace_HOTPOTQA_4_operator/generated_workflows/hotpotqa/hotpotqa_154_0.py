# Workflow ID: hotpotqa_154_0
# Benchmark: hotpotqa
# Data Indices: [112, 116]

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
            - Bridge: Connects entities across documents
            - Comparison: Compares properties
            - Compositional: Combines multiple facts
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships in parallel
        entities_list = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract entities and relationships from Document {i+1}:
                - Entities: [names, places, organizations]
                - Relationships: [how entities interact]""",
                context=""
            ) for i in range(10)]  # Assuming up to 10 documents
        )

        # Step 3: Combine entities and relationships
        combined_entities = await self.ensemble(
            instruction="Combine entities and relationships from all documents.",
            contexts_list=entities_list
        )

        # Step 4: Construct reasoning chain based on question type
        if "bridge" in question_type.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Construct reasoning chain for bridge question:
                - Identify bridge entity
                - Link documents through bridge entity
                Entities and relationships: {combined_entities}""",
                context=question_type
            )
        elif "comparison" in question_type.lower():
            reasoning_chain = await self.generate(
                instruction=f"""Construct reasoning chain for comparison question:
                - Extract properties to compare
                - Evaluate properties
                Entities and relationships: {combined_entities}""",
                context=question_type
            )
        else:  # Compositional
            reasoning_chain = await self.generate(
                instruction=f"""Construct reasoning chain for compositional question:
                - Combine multiple facts
                - Derive final answer
                Entities and relationships: {combined_entities}""",
                context=question_type
            )

        # Step 5: Validate and refine reasoning chain
        validation = await self.generate(
            instruction=f"""Validate reasoning chain:
            - Check factual correctness
            - Ensure support from documents
            Reasoning chain: {reasoning_chain}""",
            context=combined_entities
        )
        refined_chain = await self.revise(
            instruction=f"""Refine reasoning chain based on validation:
            - Fix errors
            - Add missing details
            Validation: {validation}""",
            context=reasoning_chain
        )

        # Step 6: Extract and return final answer
        final_answer = await self.generate(
            instruction=f"""Extract final answer from refined reasoning chain:
            - Short text span or yes/no response
            Refined chain: {refined_chain}""",
            context=combined_entities
        )

        return final_answer