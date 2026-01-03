# Workflow ID: hotpotqa_113_0
# Benchmark: hotpotqa
# Data Indices: [419]

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
            - Is it a bridge question (connecting entities across documents)?
            - Is it a comparison question (comparing properties across documents)?
            - Is it a compositional question (combining multiple facts)?
            Provide clear reasoning for your classification.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities_and_relationships = await self.generate(
            instruction=f"""Extract all relevant entities and relationships from the documents:
            - Identify named entities (people, places, organizations).
            - Identify relationships between entities (e.g., 'works for', 'directed by').
            - Focus on information relevant to the question type: {question_type}.
            Format as structured list.""",
            context=question_type
        )

        # Step 3: Build multiple reasoning chains in parallel
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct a reasoning chain connecting the entities:
                - Start with the question: {self.problem_text}
                - Use the extracted entities and relationships: {entities_and_relationships}
                - Follow a logical sequence to connect the dots across documents.""",
                context=entities_and_relationships
            ),
            self.generate(
                instruction=f"""Construct an alternative reasoning chain:
                - Consider different interpretations of the question.
                - Explore indirect connections between entities.
                - Ensure the chain is plausible and supported by the documents.""",
                context=entities_and_relationships
            )
        )

        # Step 4: Resolve ambiguities using ensemble
        selected_chain = await self.ensemble(
            instruction=f"""Evaluate the reasoning chains and select the most plausible one:
            - Chain 1: {reasoning_chains[0]}
            - Chain 2: {reasoning_chains[1]}
            - Consider factual accuracy, logical consistency, and alignment with the question.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Validate and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Refine the selected reasoning chain:
            - Ensure the answer is factually correct based on the documents.
            - Remove any redundant or irrelevant information.
            - Present the answer in a concise format.""",
            context=selected_chain
        )

        # Step 6: Summarize the final answer
        final_answer = await self.summarize(
            instruction=f"""Extract the final answer from the refined reasoning chain:
            - Focus on the specific question asked.
            - Provide a short, factual answer (entity/phrase or yes/no).""",
            context=refined_answer
        )

        return final_answer