# Workflow ID: hotpotqa_76_0
# Benchmark: hotpotqa
# Data Indices: [227]

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

        # Step 1: Initial Analysis - Classify question and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Is it a bridge, comparison, or compositional question?
            - Identify all named entities (people, places, dates).
            - Highlight relationships mentioned in the question.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Bridge Entity Discovery - Find potential connections
        bridge_entities = await self.generate(
            instruction=f"""Using the initial analysis:
            {initial_analysis}
            
            Identify potential bridge entities that connect documents:
            - Search for shared entities across documents.
            - Focus on entities mentioned in the question.
            - Provide a ranked list of bridge entities with explanations.""",
            context=initial_analysis
        )

        # Step 3: Connection Validation - Validate relevance of bridge entities
        validated_connections = await self.revise(
            instruction=f"""Validate the relevance of these bridge entities:
            {bridge_entities}
            
            Ensure they directly connect to the question and documents.
            Remove irrelevant or weak connections.
            Provide a refined list of validated connections.""",
            context=bridge_entities
        )

        # Step 4: Answer Extraction - Extract precise answer spans
        # Parallelize extraction for efficiency
        extraction_tasks = []
        for entity in validated_connections.split("\n"):
            extraction_tasks.append(
                self.generate(
                    instruction=f"""Extract the precise answer for the question based on this connection:
                    {entity}
                    
                    Locate the exact sentence or phrase in the document that answers the question.
                    Ensure the answer is factually correct and verbatim from the text.""",
                    context=validated_connections
                )
            )
        extracted_answers = await asyncio.gather(*extraction_tasks)

        # Step 5: Final Synthesis - Combine results and select best answer
        final_answer = await self.ensemble(
            instruction="""Synthesize all extracted answers:
            - Select the most accurate and relevant answer.
            - Ensure the answer matches the expected format (short text span or yes/no).
            - Provide the final answer with supporting evidence.""",
            contexts_list=extracted_answers
        )

        return final_answer