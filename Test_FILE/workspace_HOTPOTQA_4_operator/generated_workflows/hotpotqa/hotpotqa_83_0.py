# Workflow ID: hotpotqa_83_0
# Benchmark: hotpotqa
# Data Indices: [166]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type and extract key entities:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities, numbers, and relationships.
            - Highlight entities directly mentioned in the question.
            Provide structured output with categories: Question Type, Entities, Relationships.""",
            context=""
        )

        # Step 2: Ensemble Voting for Question Classification
        question_hypotheses = await asyncio.gather(
            self.generate(instruction="Classify as bridge question.", context=initial_analysis),
            self.generate(instruction="Classify as comparison question.", context=initial_analysis),
            self.generate(instruction="Classify as compositional question.", context=initial_analysis)
        )
        question_type = await self.ensemble(
            instruction="Select the most likely question type based on evidence.",
            contexts_list=question_hypotheses
        )

        # Step 3: Parallel Reasoning Chains
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Build a reasoning chain for the question:
                - Connect entities across documents.
                - Follow logical relationships.
                - Ensure factual support from documents.
                Question Type: {question_type}""",
                context=initial_analysis
            ) for _ in range(3)]  # Generate 3 chains in parallel
        )

        # Step 4: Validate and Refine Reasoning Chains
        refined_chains = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity and ensure logical consistency.",
                context=chain
            ) for chain in reasoning_chains]
        )

        # Step 5: Select Best Reasoning Chain
        best_chain = await self.ensemble(
            instruction="Select the most coherent and factually supported reasoning chain.",
            contexts_list=refined_chains
        )

        # Step 6: Answer Extraction
        condensed_chain = await self.summarize(
            instruction="Condense the reasoning chain into key points while preserving factual accuracy.",
            context=best_chain
        )
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span from the condensed reasoning chain:
            - Match the phrasing of the question.
            - Ensure the answer is verbatim from the documents.
            Condensed Chain: {condensed_chain}""",
            context=best_chain
        )

        # Step 7: Final Output
        final_output = await self.generate(
            instruction=f"""Format the final output:
            - Include the answer span.
            - Highlight supporting facts from the reasoning chain.
            - Add a confidence score based on chain coherence.
            Answer Extraction: {answer_extraction}""",
            context=condensed_chain
        )

        return final_output