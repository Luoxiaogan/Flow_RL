# Workflow ID: hotpotqa_156_0
# Benchmark: hotpotqa
# Data Indices: [367, 157]

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

        # Step 1: Initial Analysis - Classify question type and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional) 
            and extract key entities. Focus on:
            - Named entities (people, places, organizations)
            - Relationships between entities
            - Question-specific keywords""",
            context=""
        )

        # Step 2: Parallel Fact Extraction - Process all documents in parallel
        documents = re.findall(r"Document \d+:.*?(?=Document|\*\*\*QUESTION)", self.problem_text, re.DOTALL)
        document_tasks = [
            self.generate(
                instruction=f"""Extract relevant facts from this document:
                - Key entities and relationships
                - Facts related to the question entities
                Document Content: {doc}""",
                context=initial_analysis
            ) for doc in documents
        ]
        extracted_facts = await asyncio.gather(*document_tasks)

        # Step 3: Bridge Entity Identification - Identify shared entities across documents
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities that connect documents:
            - Shared named entities
            - Common relationships or themes
            Provide a ranked list of bridge entities.""",
            contexts_list=extracted_facts
        )

        # Step 4: Reasoning Chain Construction - Build the reasoning path
        reasoning_chain = await self.generate(
            instruction=f"""Using the bridge entities: {bridge_entities}
            Construct a reasoning chain to answer the question:
            - Connect facts across documents
            - Follow logical relationships
            - Ensure each step is supported by evidence""",
            context="\n".join(extracted_facts)
        )

        # Step 5: Validation and Refinement - Validate the reasoning chain
        refined_answer = await self.revise(
            instruction="""Validate the reasoning chain and refine the answer:
            - Check factual accuracy
            - Ensure precision (exact text spans or yes/no)
            - Resolve ambiguities""",
            context=reasoning_chain
        )

        # Step 6: Final Synthesis - Extract the final answer
        final_answer = await self.summarize(
            instruction="""Condense the reasoning chain into a concise answer:
            - Extract the precise answer span
            - Format as short text or yes/no""",
            context=refined_answer
        )

        return final_answer