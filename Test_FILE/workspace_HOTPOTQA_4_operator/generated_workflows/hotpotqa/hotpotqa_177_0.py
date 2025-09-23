# Workflow ID: hotpotqa_177_0
# Benchmark: hotpotqa
# Data Indices: [36, 16]

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

        # Step 1: Initial Analysis
        classification_task = self.generate(
            instruction="""Classify the question type:
            1. Is it a bridge question (connecting entities)?
            2. Is it a comparison question (evaluating properties)?
            3. Is it a compositional question (combining facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        entity_extraction_task = self.generate(
            instruction="""Extract all named entities and relationships from the context documents:
            - People, places, organizations
            - Key relationships and attributes
            Format as a structured list.""",
            context=""
        )

        classification, entities = await asyncio.gather(classification_task, entity_extraction_task)

        # Step 2: Bridge Entity Identification (if applicable)
        if "bridge" in classification.lower():
            bridge_entities = await self.generate(
                instruction=f"""Identify potential bridge entities based on the extracted entities:
                {entities}
                Find entities that appear in multiple documents and are relevant to the question.""",
                context=classification
            )
            validated_entities = await self.revise(
                instruction="Validate the relevance of each bridge entity to the question.",
                context=bridge_entities
            )
            bridge_entities = validated_entities

        # Step 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain using the identified entities:
            {bridge_entities if 'bridge' in classification.lower() else entities}
            Trace how information flows from one document to another to answer the question.""",
            context=entities
        )

        # Step 4: Handle Comparison and Compositional Questions
        if "comparison" in classification.lower():
            comparison_results = await asyncio.gather(
                self.generate(
                    instruction="Extract relevant properties for comparison from the first document.",
                    context=reasoning_chain
                ),
                self.generate(
                    instruction="Extract relevant properties for comparison from the second document.",
                    context=reasoning_chain
                )
            )
            answer = await self.ensemble(
                instruction="Compare the extracted properties and determine the correct answer.",
                contexts_list=comparison_results
            )
        elif "compositional" in classification.lower():
            compositional_answer = await self.generate(
                instruction="Combine the extracted facts iteratively to derive the final answer.",
                context=reasoning_chain
            )
            answer = compositional_answer
        else:
            answer = await self.generate(
                instruction="Extract the precise answer span from the final document in the reasoning chain.",
                context=reasoning_chain
            )

        # Step 5: Final Validation
        final_answer = await self.revise(
            instruction="Validate the extracted answer against the supporting facts and refine if necessary.",
            context=answer
        )

        return final_answer