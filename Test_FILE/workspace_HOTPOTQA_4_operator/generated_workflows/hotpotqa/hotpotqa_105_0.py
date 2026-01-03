# Workflow ID: hotpotqa_105_0
# Benchmark: hotpotqa
# Data Indices: [172]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question and perform the following tasks:
            1. Classify the question type as one of the following:
               - Bridge: Requires connecting documents through shared entities.
               - Comparison: Involves comparing properties across documents.
               - Compositional: Combines multiple facts to derive an answer.
            2. Extract all named entities, numbers, and relationships mentioned in the question.
            Provide a structured response with clear labels.""",
            context=""
        )

        # Parse initial analysis to determine question type and entities
        question_type = "Bridge"  # Default assumption; refine based on actual result
        entities = []

        if "Bridge" in initial_analysis:
            question_type = "Bridge"
        elif "Comparison" in initial_analysis:
            question_type = "Comparison"
        elif "Compositional" in initial_analysis:
            question_type = "Compositional"

        # Extract entities from the initial analysis
        entities = [entity.strip() for entity in initial_analysis.split("Entities:")[-1].split(",") if entity.strip()]

        # Step 2: Entity Matching - Match entities to documents
        matched_documents = await asyncio.gather(
            *[self.generate(
                instruction=f"""Identify which document(s) contain information about the entity '{entity}'.
                Provide the document titles and relevant sentences.""",
                context=""
            ) for entity in entities]
        )

        # Flatten matched documents into a single list
        matched_docs_flat = [doc for doc_list in matched_documents for doc in doc_list.split("\n") if doc]

        # Step 3: Reasoning Chain Construction - Build reasoning chains
        reasoning_chains = []
        if question_type == "Bridge":
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Using the information from the matched documents, build a reasoning chain that connects '{entities[0]}' to '{entities[1]}'.
                    Trace the logical flow of information across documents.""",
                    context="\n".join(matched_docs_flat)
                )]
            )
        elif question_type == "Comparison":
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Compare the properties of '{entities[0]}' and '{entities[1]}' based on the information from the matched documents.
                    Identify the key differences and similarities.""",
                    context="\n".join(matched_docs_flat)
                )]
            )
        elif question_type == "Compositional":
            reasoning_chains = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Combine the facts about '{entities[0]}', '{entities[1]}', and any other relevant entities to derive the answer.
                    Ensure the reasoning is coherent and logically consistent.""",
                    context="\n".join(matched_docs_flat)
                )]
            )

        # Step 4: Answer Synthesis - Extract and refine the final answer
        synthesized_answer = await self.summarize(
            instruction="Condense the reasoning chain into a concise answer that directly addresses the question.",
            context="\n".join(reasoning_chains)
        )

        refined_answer = await self.revise(
            instruction="Ensure the answer is factually correct, precise, and supported by evidence from the documents.",
            context=synthesized_answer
        )

        return refined_answer