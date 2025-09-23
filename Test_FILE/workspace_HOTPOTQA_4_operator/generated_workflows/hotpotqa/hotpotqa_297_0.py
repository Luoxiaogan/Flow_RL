# Workflow ID: hotpotqa_297_0
# Benchmark: hotpotqa
# Data Indices: [39]

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
            instruction="""Classify the question into one of the following categories:
            1. Bridge: Requires connecting entities across documents.
            2. Comparison: Involves comparing properties across documents.
            3. Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_tasks = [
            self.generate(
                instruction=f"""Extract named entities and relationships from Document {i+1}.
                Focus on people, places, dates, and key concepts.
                Format as a structured list.""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        entities_results = await asyncio.gather(*entities_tasks)
        entities_summary = "\n".join(entities_results)

        # Step 3: Identify bridge entities
        bridge_entities = await self.generate(
            instruction=f"""Identify entities shared across multiple documents.
            Use the extracted entities:
            {entities_summary}
            Focus on entities that connect the reasoning chain.""",
            context=question_type
        )

        # Step 4: Build reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Construct a reasoning chain using the identified entities:
            {bridge_entities}
            Trace how one piece of information leads to another across documents.""",
            context=entities_summary
        )
        refined_chain = await self.revise(
            instruction="Ensure the reasoning chain is logically consistent and complete.",
            context=reasoning_chain
        )

        # Step 5: Extract precise answer
        answer_candidates = await asyncio.gather(
            self.summarize(
                instruction="Extract the exact answer span from the relevant document.",
                context=refined_chain
            ),
            self.generate(
                instruction="If the answer is ambiguous, provide alternative interpretations.",
                context=refined_chain
            )
        )
        final_answer = await self.ensemble(
            instruction="Select the most accurate and concise answer.",
            contexts_list=answer_candidates
        )

        # Step 6: Validate and handle edge cases
        validation = await self.generate(
            instruction="Validate the final answer against the reasoning chain and documents.",
            context=final_answer
        )
        if "error" in validation.lower():
            final_answer = await self.revise(
                instruction="Correct any issues identified during validation.",
                context=final_answer
            )

        return final_answer