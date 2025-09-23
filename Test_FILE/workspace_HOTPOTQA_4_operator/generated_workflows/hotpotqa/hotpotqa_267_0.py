# Workflow ID: hotpotqa_267_0
# Benchmark: hotpotqa
# Data Indices: [103, 211]

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
        import re

        # Step 1: Analyze the question type and structure
        question_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge, comparison, or compositional question?
            2. Identify key entities and relationships mentioned in the question.
            3. Determine the expected answer format (short text span or yes/no).
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel analysis of context documents
        document_titles = re.findall(r'Document \d+: (.+)', self.problem_text)
        document_texts = re.split(r'Document \d+: .+\n', self.problem_text)[1:]
        document_analyses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract entities, relationships, and potential bridge entities from this document:
                Title: {title}
                Content: {text}""",
                context=""
            ) for title, text in zip(document_titles, document_texts)]
        )

        # Step 3: Synthesize entities and relationships across documents
        synthesis = await self.ensemble(
            instruction="""Merge the analyses of individual documents:
            - Identify shared entities that connect documents (bridge entities).
            - Construct a reasoning chain that links these entities.
            - Highlight supporting facts from different documents.
            Provide a unified summary of the connections.""",
            contexts_list=document_analyses
        )

        # Step 4: Validate the reasoning chain
        validated_chain = await self.revise(
            instruction="""Validate the reasoning chain for factual correctness and logical coherence:
            - Cross-reference all supporting facts with the original documents.
            - Correct any gaps or inconsistencies in the chain.
            - Ensure the chain leads to a precise answer.""",
            context=synthesis
        )

        # Step 5: Extract the final answer
        final_answer = await self.summarize(
            instruction="""Extract the precise answer span from the validated reasoning chain:
            - Ensure the answer matches the expected format (short text span or yes/no).
            - Include only the exact answer without additional explanation.""",
            context=validated_chain
        )

        return final_answer