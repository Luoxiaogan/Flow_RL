# Workflow ID: hotpotqa_115_0
# Benchmark: hotpotqa
# Data Indices: [351, 20]

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
            and extract key entities mentioned in the question. 
            Provide structured output including:
            - Question Type: [bridge/comparison/compositional]
            - Key Entities: [list of entities]
            - Expected Answer Format: [yes/no/short text span]""",
            context=""
        )

        # Step 2: Document Relevance Filtering - Identify relevant documents
        relevant_docs = await self.generate(
            instruction=f"""Based on the following analysis:
            {initial_analysis}
            
            Identify which documents are relevant to the question by matching key entities or topics. 
            Rank documents by relevance and provide a list of top candidates.""",
            context=initial_analysis
        )

        # Step 3: Bridge Entity Identification - Find shared entities or relationships
        bridge_entities = await self.generate(
            instruction=f"""Using the relevant documents:
            {relevant_docs}
            
            Identify shared entities or relationships (bridge entities) that connect the documents. 
            Propose potential bridge entities and explain how they connect the documents.""",
            context=relevant_docs
        )

        # Validate bridge entities
        validated_entities = await self.revise(
            instruction="""Verify the proposed bridge entities:
            - Ensure they indeed connect the relevant documents
            - Check for ambiguity or multiple interpretations
            - Provide confidence scores for each entity""",
            context=bridge_entities
        )

        # Step 4: Reasoning Chain Construction - Build explicit reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the validated bridge entities:
            {validated_entities}
            
            Construct an explicit reasoning chain by connecting facts from different documents. 
            Follow the chain step-by-step to arrive at the final document containing the answer.""",
            context=validated_entities
        )

        # Refine reasoning chain
        refined_chain = await self.revise(
            instruction="""Refine the reasoning chain:
            - Ensure logical consistency between steps
            - Add missing details or clarify ambiguous steps
            - Verify factual accuracy of each connection""",
            context=reasoning_chain
        )

        # Step 5: Answer Extraction - Extract precise answer span
        extracted_answer = await self.generate(
            instruction=f"""From the final document in the reasoning chain:
            {refined_chain}
            
            Extract the precise answer span that directly answers the question. 
            Ensure the answer matches the expected format (yes/no/short text span).""",
            context=refined_chain
        )

        # Condense answer
        final_answer = await self.summarize(
            instruction="""Condense the extracted answer into the required format:
            - Short text span or yes/no response
            - Remove any extraneous details""",
            context=extracted_answer
        )

        # Step 6: Final Validation - Validate answer against question and supporting facts
        validation_result = await self.ensemble(
            instruction="""Validate the final answer:
            - Ensure it is factually correct based on the documents
            - Check alignment with the question and supporting facts
            - Compare with alternative answers if applicable
            Select the best answer based on validation criteria.""",
            contexts_list=[final_answer, initial_analysis, refined_chain]
        )

        return validation_result