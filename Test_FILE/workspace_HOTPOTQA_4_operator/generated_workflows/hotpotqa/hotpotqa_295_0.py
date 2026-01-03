# Workflow ID: hotpotqa_295_0
# Benchmark: hotpotqa
# Data Indices: [446, 122]

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
            instruction="""Classify the question into one of the following types:
            - Bridge Question: Connects information through shared entities.
            - Comparison Question: Compares properties across documents.
            - Compositional Question: Combines multiple facts to derive an answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract entities and relationships in parallel
        entities_task = self.generate(
            instruction="Extract all named entities, relationships, and key phrases from the documents.",
            context=""
        )
        relationships_task = self.generate(
            instruction="Identify relationships between entities and their relevance to the question.",
            context=""
        )
        entities, relationships = await asyncio.gather(entities_task, relationships_task)

        # Step 3: Build reasoning chains
        reasoning_chains = await self.generate(
            instruction=f"""Using the extracted entities ({entities}) and relationships ({relationships}),
            construct reasoning chains that connect the documents to answer the question.
            Ensure each chain is logically consistent and factually supported.""",
            context=f"{entities}\n{relationships}"
        )

        # Step 4: Validate and refine reasoning chains
        refined_chains = await self.revise(
            instruction="Critically evaluate the reasoning chains for validity and completeness. Refine as needed.",
            context=reasoning_chains
        )

        # Step 5: Extract and validate the answer
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Extract the precise answer from the refined reasoning chains ({refined_chains}).
                Ensure the answer is supported by the documents and matches the question format.""",
                context=refined_chains
            ),
            self.generate(
                instruction="Consider alternative interpretations of the question and provide additional plausible answers.",
                context=refined_chains
            )
        )

        # Step 6: Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and well-supported answer from the candidates.",
            contexts_list=answer_candidates
        )

        return final_answer