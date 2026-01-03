# Workflow ID: hotpotqa_241_0
# Benchmark: hotpotqa
# Data Indices: [51]

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

        # Step 1: Classify question type and extract key entities
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type and extract key entities:
            - Identify if it's a bridge, comparison, or compositional question.
            - Extract all named entities, relationships, and specific constraints.
            - Provide a structured classification of the question type.""",
            context=""
        )

        # Step 2: Parallel document analysis to extract relevant information
        documents = re.findall(r'Document \d+:.*?(?=\n\n|$)', self.problem_text, re.DOTALL)
        document_tasks = [
            self.generate(
                instruction=f"""Extract relevant entities and relationships from this document:
                - Focus on entities and facts related to the question.
                - Highlight any shared entities or relationships with other documents.""",
                context=doc
            ) for doc in documents
        ]
        document_results = await asyncio.gather(*document_tasks)

        # Step 3: Synthesize document information to identify bridge entities
        synthesized_entities = await self.ensemble(
            instruction="""Identify overlapping entities and relationships across documents:
            - Find shared entities that connect documents.
            - Highlight relationships that form potential reasoning chains.""",
            contexts_list=document_results
        )

        # Step 4: Construct reasoning chain based on question type
        reasoning_chain = await self.generate(
            instruction=f"""Using the following information:
            Question Analysis: {question_analysis}
            Synthesized Entities: {synthesized_entities}
            
            Construct an explicit reasoning chain:
            - Link entities and relationships across documents.
            - Ensure the chain leads to the answer.""",
            context=""
        )

        # Step 5: Refine reasoning chain and extract precise answer
        refined_answer = await self.revise(
            instruction=f"""Refine the reasoning chain to ensure accuracy:
            - Verify all connections are factually correct.
            - Extract the precise answer as a short text span or yes/no response.""",
            context=reasoning_chain
        )

        # Step 6: Final validation and output
        final_output = await self.generate(
            instruction=f"""Validate the extracted answer:
            - Ensure it is directly supported by the documents.
            - Format the answer as a short text span or yes/no response.""",
            context=refined_answer
        )

        return final_output.strip()