# Workflow ID: hotpotqa_268_0
# Benchmark: hotpotqa
# Data Indices: [285, 99]

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
        classification = await self.generate(
            instruction="""Classify the question type:
            - Is it a bridge question, comparison question, or compositional question?
            - What entities or attributes are involved?
            - What is the expected answer format?
            Provide a structured analysis.""",
            context=""
        )

        # Step 2: Extract key entities and relationships from documents
        entities_tasks = [
            self.generate(
                instruction=f"""Extract all named entities, relationships, and constraints from Document {i+1}.
                Focus on entities and relationships relevant to the question type identified earlier: {classification}""",
                context=""
            ) for i in range(10)  # Assuming up to 10 documents
        ]
        entities_results = await asyncio.gather(*entities_tasks)

        # Step 3: Build reasoning chains across documents
        reasoning_chains = await self.generate(
            instruction=f"""Using the extracted entities and relationships:
            {entities_results}
            
            Build reasoning chains that connect the documents:
            - Identify shared entities or attributes.
            - Ensure each step in the chain is factually supported.
            - Highlight potential gaps or ambiguities.""",
            context=classification
        )

        # Step 4: Validate and refine reasoning chains
        refined_chains = await self.revise(
            instruction="""Review the reasoning chains:
            - Check for factual accuracy.
            - Resolve ambiguities or gaps.
            - Ensure the chain leads to the expected answer format.""",
            context=reasoning_chains
        )

        # Step 5: Extract precise answers from the final document
        answer_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""From Document {i+1}, extract the precise answer span:
                - Ensure it matches the reasoning chain: {refined_chains}
                - Use exact text spans without paraphrasing.""",
                context=entities_results[i]
            ) for i in range(10)]
        )

        # Step 6: Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="""Evaluate the answer candidates:
            - Select the most factually supported answer.
            - Ensure it aligns with the reasoning chain.
            - Resolve any conflicts between candidates.""",
            contexts_list=answer_candidates
        )

        return final_answer