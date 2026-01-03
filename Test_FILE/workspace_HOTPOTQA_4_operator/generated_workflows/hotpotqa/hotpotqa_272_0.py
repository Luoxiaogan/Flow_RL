# Workflow ID: hotpotqa_272_0
# Benchmark: hotpotqa
# Data Indices: [147, 275]

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
        
        # Step 1: Question Classification
        question_type = await self.generate(
            instruction="""Classify the question into one of the following types:
            1. Bridge: Connects documents through shared entities.
            2. Comparison: Evaluates properties across documents.
            3. Compositional: Combines multiple facts to derive an answer.
            Provide a clear classification and justification.""",
            context=""
        )
        
        # Step 2: Entity Extraction
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the context documents.
            Focus on entities relevant to the question type: {question_type}.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 3: Bridge Entity Identification
        bridge_entities = await self.generate(
            instruction=f"""Identify bridge entities that connect documents.
            Entities: {entities}
            Question Type: {question_type}
            List potential bridge entities and their connections.""",
            context=entities
        )
        
        # Step 4: Reasoning Chain Construction (Parallel Exploration)
        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Construct a reasoning chain for bridge entity: {entity}.
                Extract relevant facts from connected documents and explain the logical connection.""",
                context=entities
            ) for entity in bridge_entities.split("\n") if entity.strip()]
        )
        
        # Step 5: Candidate Answer Generation
        candidate_answers = await asyncio.gather(
            *[self.generate(
                instruction=f"""Generate a candidate answer based on reasoning chain: {chain}.
                Extract precise answer spans from the relevant documents.""",
                context=chain
            ) for chain in reasoning_chains]
        )
        
        # Step 6: Validation and Ensemble
        final_answer = await self.ensemble(
            instruction="""Select the best answer based on:
            1. Factual accuracy
            2. Alignment with the question
            3. Supporting evidence from documents""",
            contexts_list=candidate_answers
        )
        
        # Step 7: Refinement Loop (Optional)
        validation = await self.generate(
            instruction=f"""Validate the final answer: {final_answer}.
            Check for factual accuracy and alignment with the question.""",
            context=final_answer
        )
        if "error" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback: {validation}.
                Correct any inaccuracies or missing details.""",
                context=final_answer
            )
            return refined_answer
        
        return final_answer