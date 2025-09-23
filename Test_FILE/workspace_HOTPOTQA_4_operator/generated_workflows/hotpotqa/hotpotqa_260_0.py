# Workflow ID: hotpotqa_260_0
# Benchmark: hotpotqa
# Data Indices: [233]

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

        # Step 1: Initial Analysis - Classify question type and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the question type (bridge, comparison, compositional).
            2. Extract key entities, relationships, and constraints.
            3. Highlight potential bridge entities that connect documents.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Entity Exploration - Explore potential bridge entities
        entities = [e.strip() for e in initial_analysis.split("\n") if e.strip()]
        entity_explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"""For the entity '{entity}':
                1. Identify all documents mentioning this entity.
                2. Extract relevant facts and relationships.
                3. Assess its potential as a bridge entity.
                Provide detailed analysis.""",
                context=initial_analysis
            ) for entity in entities]
        )

        # Step 3: Entity Evaluation and Selection - Select the best bridge entity
        best_entity = await self.ensemble(
            instruction="""Evaluate the candidate bridge entities:
            1. Consider strength of connections across documents.
            2. Assess relevance to the question.
            3. Select the most promising entity.
            Provide justification for the selection.""",
            contexts_list=entity_explorations
        )

        # Step 4: Reasoning Chain Construction - Build the reasoning chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the selected bridge entity '{best_entity}':
            1. Trace connections across documents.
            2. Gather supporting facts in sequence.
            3. Construct a logical reasoning chain leading to the answer.
            Ensure the chain is complete and coherent.""",
            context=initial_analysis
        )

        # Step 5: Answer Extraction and Validation - Extract and validate the answer
        answer_extraction = await self.generate(
            instruction=f"""From the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the final document.
            Validate the answer against the reasoning chain.
            Ensure factual correctness and direct support from evidence.""",
            context=reasoning_chain
        )

        # Step 6: Final Revision - Refine the answer if needed
        final_answer = await self.revise(
            instruction="""Review the extracted answer:
            1. Verify precision and correctness.
            2. Ensure it matches the required format (short text span or yes/no).
            3. Make any necessary refinements.""",
            context=answer_extraction
        )

        return final_answer