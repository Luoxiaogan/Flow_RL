# Workflow ID: hotpotqa_25_0
# Benchmark: hotpotqa
# Data Indices: [341, 5]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities (names, places, numbers).
            3. Identify relationships between entities.
            Provide structured output with clear labels.""",
            context=""
        )

        # Phase 2: Entity Linking
        entities = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Extract entities and relationships:
            - For bridge questions, find shared entities.
            - For comparison questions, extract comparable attributes.
            - For compositional questions, identify all relevant facts.
            Organize the output by document and relationship.""",
            context=analysis
        )

        # Parallelize entity validation
        entity_validations = await asyncio.gather(
            self.generate(instruction="Validate entities against Document 1...", context=entities),
            self.generate(instruction="Validate entities against Document 2...", context=entities),
            self.generate(instruction="Validate entities against Document 3...", context=entities)
        )
        validated_entities = await self.ensemble(
            instruction="Select the most relevant entities and relationships.",
            contexts_list=entity_validations
        )

        # Phase 3: Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Construct the reasoning chain:
            Validated Entities: {validated_entities}
            
            Build step-by-step connections between documents:
            - Start with the question.
            - Use entities and relationships to connect documents.
            - Ensure each link is supported by evidence.
            Provide the full chain as output.""",
            context=validated_entities
        )

        refined_chain = await self.revise(
            instruction="Refine the reasoning chain for clarity and logical consistency.",
            context=reasoning_chain
        )

        # Phase 4: Answer Extraction
        answer = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Refined Chain: {refined_chain}
            
            Identify the exact answer span from the final document.
            Ensure the answer is factual and concise.""",
            context=refined_chain
        )

        summarized_answer = await self.summarize(
            instruction="Condense the answer into a short, factual response.",
            context=answer
        )

        # Phase 5: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the answer against the original documents:
            Summarized Answer: {summarized_answer}
            
            Check for factual correctness and completeness.
            Flag any discrepancies.""",
            context=summarized_answer
        )

        final_answer = await self.revise(
            instruction="Refine the answer based on validation feedback.",
            context=validation
        )

        return final_answer