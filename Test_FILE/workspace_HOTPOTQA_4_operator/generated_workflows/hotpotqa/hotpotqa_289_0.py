# Workflow ID: hotpotqa_289_0
# Benchmark: hotpotqa
# Data Indices: [449]

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

        # Step 1: Extract entities and relationships from all documents in parallel
        entity_extraction_instructions = """Extract all named entities, relationships, and key facts from the documents. 
        Focus on:
        - People, places, organizations, and their roles
        - Dates, events, and their significance
        - Relationships between entities (e.g., director of a movie, founder of an organization)
        Format the output as a structured list."""
        entity_extractions = await asyncio.gather(
            *[self.generate(instruction=entity_extraction_instructions, context="") for _ in range(10)]  # Assuming 10 documents
        )

        # Step 2: Identify bridge entities and construct reasoning chains
        reasoning_chain_instructions = f"""Using the extracted entities and relationships:
        {entity_extractions}
        
        Identify bridge entities that connect the documents. Then, construct a reasoning chain:
        - Start with the question and identify the target entity.
        - Trace the path through the documents using bridge entities.
        - Ensure each step in the chain is logically connected."""
        reasoning_chains = await asyncio.gather(
            *[self.generate(instruction=reasoning_chain_instructions, context=extraction) for extraction in entity_extractions]
        )

        # Step 3: Synthesize the reasoning chain into a coherent answer
        synthesis_instructions = """Synthesize the reasoning chains into a single coherent answer:
        - Combine overlapping facts and resolve conflicts.
        - Ensure the answer directly addresses the question.
        - Highlight supporting facts from different documents."""
        synthesized_answer = await self.ensemble(
            instruction=synthesis_instructions,
            contexts_list=reasoning_chains
        )

        # Step 4: Validate and refine the answer
        validation_instructions = f"""Validate the synthesized answer:
        {synthesized_answer}
        
        Check:
        - Factual correctness based on the documents
        - Logical consistency of the reasoning chain
        - Precision of the answer (exact spans, not paraphrases)"""
        validated_answer = await self.revise(
            instruction=validation_instructions,
            context=synthesized_answer
        )

        # Step 5: Final refinement (optional feedback loop)
        refinement_instructions = """Refine the validated answer:
        - Improve clarity and conciseness
        - Add missing details if necessary
        - Ensure the format matches the expected answer type (short text span or yes/no)."""
        final_answer = await self.revise(
            instruction=refinement_instructions,
            context=validated_answer
        )

        return final_answer