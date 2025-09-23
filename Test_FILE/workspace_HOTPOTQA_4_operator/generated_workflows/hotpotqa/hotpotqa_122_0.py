# Workflow ID: hotpotqa_122_0
# Benchmark: hotpotqa
# Data Indices: [6, 257]

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
            instruction="""Analyze the question and classify it into one of the following types:
            1. Bridge: Requires connecting documents through shared entities.
            2. Comparison: Requires comparing properties across documents.
            3. Compositional: Requires combining multiple facts to derive the answer.
            Provide a clear classification and explain your reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Based on the question type ({question_type}), extract all relevant entities and relationships:
            - Entities: Names, dates, locations, etc.
            - Relationships: How entities are connected across documents.
            Format as a structured list.""",
            context=""
        )
        refined_entities = await self.revise(
            instruction="Validate and refine the extracted entities. Remove any irrelevant or duplicate entries.",
            context=entities
        )

        # Step 3: Build reasoning chains (parallel processing)
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Using the entity {entity}, build a reasoning chain that connects the documents:
                - Start with the entity in one document.
                - Follow its connections to other documents.
                - End with a potential answer to the question.""",
                context=refined_entities
            ) for entity in refined_entities.split("\n") if entity.strip()]
        )

        # Step 4: Synthesize the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""Evaluate the reasoning chains and select the most plausible one:
            - Does the chain logically connect the documents?
            - Does it lead to a valid answer?
            - Is it supported by the context documents?""",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the final answer
        final_answer = await self.generate(
            instruction=f"""From the reasoning chain ({best_chain}), extract the precise answer span:
            - Locate the exact sentence or phrase that answers the question.
            - Ensure the answer is factually correct and directly supported by the documents.""",
            context=best_chain
        )

        # Step 6: Validate and refine the final answer
        validated_answer = await self.revise(
            instruction="Verify the accuracy of the final answer. Correct any errors or ambiguities.",
            context=final_answer
        )

        return validated_answer