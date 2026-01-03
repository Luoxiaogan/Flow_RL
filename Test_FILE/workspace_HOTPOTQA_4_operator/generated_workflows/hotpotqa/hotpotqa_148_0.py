# Workflow ID: hotpotqa_148_0
# Benchmark: hotpotqa
# Data Indices: [400]

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
            instruction="""Classify the question type:
            - Bridge: Requires connecting information through shared entities.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and identify connections (parallelized)
        entity_extraction_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: People, places, organizations, etc.
            - Relationships: How entities are connected across documents.
            Format as structured output.""",
            context=""
        )
        connection_identification_task = self.generate(
            instruction="""Identify shared entities that connect multiple documents:
            - Shared entities: Names, dates, events, etc., appearing in more than one document.
            - Connections: How these entities link information together.
            Focus on entities relevant to the question.""",
            context=classification
        )
        entities, connections = await asyncio.gather(entity_extraction_task, connection_identification_task)

        # Step 3: Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the extracted entities and connections:
            Entities: {entities}
            Connections: {connections}

            Construct the reasoning chain:
            - Trace how information flows from one document to another.
            - Identify intermediate steps leading to the answer.
            - Ensure the chain is logically consistent and factually accurate.""",
            context=classification
        )

        # Step 4: Extract the answer (conditional branching based on classification)
        if "bridge" in classification.lower():
            answer = await self.generate(
                instruction=f"""Extract the precise answer span from the final document:
                Reasoning Chain: {reasoning_chain}
                
                Focus on:
                - Exact phrases or entities that answer the question.
                - Supporting evidence from the reasoning chain.""",
                context=reasoning_chain
            )
        elif "comparison" in classification.lower():
            answer_candidates = await asyncio.gather(
                self.generate(instruction="Compare property X across documents...", context=reasoning_chain),
                self.generate(instruction="Compare property Y across documents...", context=reasoning_chain)
            )
            answer = await self.ensemble(
                instruction="Select the most accurate comparison result.",
                contexts_list=answer_candidates
            )
        else:  # Compositional
            answer = await self.generate(
                instruction=f"""Combine multiple facts to derive the answer:
                Reasoning Chain: {reasoning_chain}
                
                Focus on:
                - Logical synthesis of facts.
                - Precise answer span supported by the text.""",
                context=reasoning_chain
            )

        # Step 5: Refine the answer (optional but recommended)
        refined_answer = await self.revise(
            instruction="""Ensure the answer is:
            - Factually correct.
            - Precisely extracted from the text.
            - Concise and directly responsive to the question.""",
            context=answer
        )

        return refined_answer