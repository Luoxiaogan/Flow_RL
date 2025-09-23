# Workflow ID: hotpotqa_37_0
# Benchmark: hotpotqa
# Data Indices: [487, 0]

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
            - Bridge: Requires connecting entities across documents
            - Comparison: Requires comparing properties across documents
            - Compositional: Requires combining multiple facts
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        extraction_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            extraction_tasks.append(
                self.generate(
                    instruction=f"""Extract named entities and relationships from Document {i}.
                    Format as structured list:
                    - Entities: [names and roles]
                    - Relationships: [connections between entities]""",
                    context=""
                )
            )
        extracted_data = await asyncio.gather(*extraction_tasks)

        # Step 3: Identify bridge entities or comparable properties
        if "bridge" in classification.lower():
            bridge_entities = await self.generate(
                instruction=f"""Identify entities that appear in multiple documents.
                Use the extracted data: {extracted_data}
                Focus on entities that connect the reasoning chain.""",
                context=classification
            )
        elif "comparison" in classification.lower():
            comparable_properties = await self.generate(
                instruction=f"""Identify properties that can be compared across documents.
                Use the extracted data: {extracted_data}
                Focus on numerical or categorical properties.""",
                context=classification
            )
        else:  # Compositional
            compositional_facts = await self.generate(
                instruction=f"""Identify facts that can be combined to answer the question.
                Use the extracted data: {extracted_data}
                Focus on logical connections between facts.""",
                context=classification
            )

        # Step 4: Build reasoning chains in parallel
        reasoning_chains = []
        if "bridge" in classification.lower():
            for entity in bridge_entities.split("\n"):
                reasoning_chains.append(
                    self.generate(
                        instruction=f"""Build a reasoning chain starting with entity: {entity}.
                        Use the extracted data: {extracted_data}
                        Follow connections between documents.""",
                        context=classification
                    )
                )
        elif "comparison" in classification.lower():
            for prop in comparable_properties.split("\n"):
                reasoning_chains.append(
                    self.generate(
                        instruction=f"""Compare property: {prop} across documents.
                        Use the extracted data: {extracted_data}
                        Provide a clear comparison.""",
                        context=classification
                    )
                )
        else:  # Compositional
            for fact in compositional_facts.split("\n"):
                reasoning_chains.append(
                    self.generate(
                        instruction=f"""Combine fact: {fact} with other facts.
                        Use the extracted data: {extracted_data}
                        Derive a logical conclusion.""",
                        context=classification
                    )
                )
        chains = await asyncio.gather(*reasoning_chains)

        # Step 5: Validate reasoning chains
        validated_chains = []
        for chain in chains:
            validation = await self.generate(
                instruction=f"""Validate this reasoning chain against supporting facts:
                Chain: {chain}
                Extracted Data: {extracted_data}
                Ensure all steps are factually correct.""",
                context=classification
            )
            if "valid" in validation.lower():
                validated_chains.append(chain)

        # Step 6: Ensemble evaluation to select the best answer
        final_answer = await self.ensemble(
            instruction="""Select the best-supported answer from the validated chains.
            Consider factual accuracy, clarity, and completeness.""",
            contexts_list=validated_chains
        )

        return final_answer