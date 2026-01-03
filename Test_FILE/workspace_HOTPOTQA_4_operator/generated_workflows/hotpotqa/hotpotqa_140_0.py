# Workflow ID: hotpotqa_140_0
# Benchmark: hotpotqa
# Data Indices: [475, 58]

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

        # Step 1: Classify the question type and extract key terms
        classification = await self.generate(
            instruction="""Classify the question type and extract key terms:
            - Is it a bridge question, comparison question, or compositional question?
            - Identify all named entities, relationships, and target properties.
            - Provide structured output with categories:
                - Question Type: [classification]
                - Key Terms: [list of terms]
                - Target Property: [what we're solving for]""",
            context=""
        )

        # Step 2: Perform parallel exploration of term interpretations
        key_terms = await self.generate(
            instruction=f"""From the classification: {classification}
            Identify possible interpretations of each key term:
            - For each term, list potential meanings (e.g., 'Strange Magic' as a film, song, or book).
            - Include relevant document titles and sentences supporting each interpretation.""",
            context=classification
        )
        interpretations = key_terms.split("\n")
        exploration_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Explore interpretation: {interp}
                - Identify bridge entities connecting documents.
                - Build reasoning chain to answer the question.
                - Extract supporting facts from documents.""",
                context=key_terms
            ) for interp in interpretations]
        )

        # Step 3: Select the best-supported interpretation
        best_interpretation = await self.ensemble(
            instruction="""Select the most supported interpretation:
            - Evaluate each reasoning chain for completeness and factual accuracy.
            - Choose the interpretation with the strongest evidence.""",
            contexts_list=exploration_results
        )

        # Step 4: Extract precise answer span and validate
        answer_span = await self.generate(
            instruction=f"""From the selected interpretation: {best_interpretation}
            - Extract the precise answer span (entity/phrase or yes/no).
            - Validate the answer against supporting facts from documents.
            - Ensure the answer is factually correct and directly addresses the question.""",
            context=best_interpretation
        )

        # Step 5: Summarize the reasoning chain and supporting facts
        summary = await self.summarize(
            instruction="""Summarize the reasoning chain and supporting facts:
            - Highlight key steps in the reasoning process.
            - List supporting facts from different documents.
            - Ensure the summary is concise and complete.""",
            context=answer_span
        )

        return {
            "answer": answer_span.strip(),
            "reasoning_chain": summary.strip()
        }