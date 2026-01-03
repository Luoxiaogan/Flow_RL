# Workflow ID: hotpotqa_95_0
# Benchmark: hotpotqa
# Data Indices: [365, 482]

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

        # Step 1: Problem Analysis and Question Classification
        problem_analysis = await self.generate(
            instruction="""Analyze the problem structure and classify the question type:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify key entities and relationships mentioned in the question.
            - Provide a structured classification.""",
            context=""
        )

        # Step 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and constraints from the context documents:
            - Entities: Names, organizations, locations, dates, etc.
            - Relationships: Connections between entities (e.g., 'is a', 'works for').
            - Constraints: Any conditions or limitations mentioned.
            Problem Analysis: {problem_analysis}""",
            context=""
        )

        # Step 3: Reasoning Chain Construction
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct reasoning chains for bridge questions:
                - Identify shared entities across documents.
                - Follow connections to answer the question.
                Entities: {entities}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct reasoning chains for comparison questions:
                - Evaluate properties of entities mentioned in the question.
                - Compare them based on the given criteria.
                Entities: {entities}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Construct reasoning chains for compositional questions:
                - Combine multiple facts to derive the answer.
                - Ensure logical consistency across steps.
                Entities: {entities}""",
                context=entities
            )
        )

        # Step 4: Synthesize and Select Best Reasoning Chain
        selected_chain = await self.ensemble(
            instruction="""Evaluate and select the most promising reasoning chain:
            - Check for factual correctness and supporting evidence.
            - Prioritize chains with strong connections between entities.
            - Ensure the chain leads to a precise answer.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span from the final document in the reasoning chain:
            - Ensure the answer matches the supporting facts verbatim.
            - Avoid paraphrasing or generalizing.
            Selected Chain: {selected_chain}""",
            context=selected_chain
        )

        # Step 6: Refine Answer if Necessary
        refined_answer = await self.revise(
            instruction=f"""Refine the extracted answer:
            - Validate against supporting facts.
            - Improve clarity and precision if needed.
            Extracted Answer: {answer_extraction}""",
            context=answer_extraction
        )

        return refined_answer