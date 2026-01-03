# Workflow ID: hotpotqa_131_0
# Benchmark: hotpotqa
# Data Indices: [270]

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
            - Bridge: Requires connecting information across documents via shared entities.
            - Comparison: Involves comparing properties or attributes across documents.
            - Compositional: Combines multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Identify potential bridge entities (if applicable)
        if "bridge" in question_type.lower():
            bridge_entities = await self.generate(
                instruction=f"""Based on the question classification ({question_type}), identify potential bridge entities that connect the documents.
                - Entities should be explicitly mentioned in the question or documents.
                - Rank entities by relevance and likelihood of forming a valid reasoning chain.""",
                context=question_type
            )

            # Validate bridge entities by checking their presence across documents
            validation_tasks = [
                self.generate(
                    instruction=f"""Verify if the bridge entity '{entity.strip()}' is present in at least two documents.
                    - Provide supporting sentences from the documents.
                    - If not found, explain why it might be invalid.""",
                    context=bridge_entities
                )
                for entity in bridge_entities.split("\n") if entity.strip()
            ]
            validations = await asyncio.gather(*validation_tasks)

            # Select the most valid bridge entity
            best_entity = await self.ensemble(
                instruction="Select the most valid bridge entity based on document support and relevance.",
                contexts_list=validations
            )

            # Step 3: Construct reasoning chain using the selected bridge entity
            reasoning_chain = await self.generate(
                instruction=f"""Using the bridge entity '{best_entity}', construct a reasoning chain:
                - Start with facts from one document.
                - Use these facts to query other documents for additional information.
                - Continue until the final answer is reached.
                Provide a detailed chain of reasoning.""",
                context=best_entity
            )

        else:
            # Handle comparison or compositional questions
            reasoning_chain = await self.generate(
                instruction=f"""Based on the question classification ({question_type}), construct a reasoning chain:
                - For comparison questions, extract comparable properties and analyze differences.
                - For compositional questions, combine relevant facts to derive the answer.
                Provide a detailed chain of reasoning.""",
                context=question_type
            )

        # Step 4: Extract and refine the final answer
        extracted_answer = await self.summarize(
            instruction=f"""Extract the precise answer from the reasoning chain:
            - Ensure the answer is a short text span or yes/no response.
            - Maintain factual correctness and traceability to the documents.""",
            context=reasoning_chain
        )

        refined_answer = await self.revise(
            instruction="""Refine the extracted answer for clarity and correctness:
            - Verify factual accuracy against the documents.
            - Ensure the answer matches the expected format.""",
            context=extracted_answer
        )

        return refined_answer