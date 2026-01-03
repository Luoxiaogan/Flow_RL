# Workflow ID: hotpotqa_304_0
# Benchmark: hotpotqa
# Data Indices: [370]

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
            instruction="""Analyze the question and classify its type:
            - Bridge: Requires connecting entities across documents.
            - Comparison: Involves comparing properties across documents.
            - Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Extract entities from all documents in parallel
        entity_extraction_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            entity_extraction_tasks.append(
                self.generate(
                    instruction=f"""Extract all named entities, relationships, and constraints from Document {i+1}.
                    Format as a structured list:
                    - Entities: [names, roles, descriptions]
                    - Relationships: [connections between entities]
                    - Constraints: [conditions or limitations]""",
                    context=""
                )
            )
        extracted_entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Identify bridge entities and build reasoning chains
        bridge_entities = await self.ensemble(
            instruction="""Identify shared entities that connect multiple documents.
            - Match entities based on name, role, and context.
            - Rank matches by confidence.
            Select the most promising bridge entities.""",
            contexts_list=extracted_entities
        )

        reasoning_chains = await self.generate(
            instruction=f"""Using the identified bridge entities:
            {bridge_entities}
            
            Build reasoning chains that connect the documents:
            - Trace logical relationships between entities.
            - Validate each step for factual consistency.
            - Highlight key supporting facts.""",
            context=bridge_entities
        )

        # Step 4: Extract and refine the answer
        raw_answer = await self.generate(
            instruction=f"""From the reasoning chains:
            {reasoning_chains}
            
            Extract the precise answer to the question:
            - Locate the exact sentence or phrase containing the answer.
            - Ensure the answer is factually correct.
            - Format the answer as required (short text span or yes/no).""",
            context=reasoning_chains
        )

        refined_answer = await self.revise(
            instruction=f"""Refine the extracted answer:
            {raw_answer}
            
            Cross-check with supporting facts and ensure clarity.
            Correct any errors or ambiguities.""",
            context=raw_answer
        )

        # Step 5: Summarize the reasoning chain
        summary = await self.summarize(
            instruction=f"""Condense the reasoning chain into a concise explanation:
            {reasoning_chains}
            
            Include only the key steps and supporting facts.""",
            context=reasoning_chains
        )

        return {
            "answer": refined_answer,
            "reasoning_summary": summary
        }