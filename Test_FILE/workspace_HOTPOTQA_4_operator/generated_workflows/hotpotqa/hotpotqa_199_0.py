# Workflow ID: hotpotqa_199_0
# Benchmark: hotpotqa
# Data Indices: [48]

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
        import re

        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem into one of the following types:
            - Bridge: Connects entities across documents (e.g., "What nationality is the director of [movie]?")
            - Comparison: Compares properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional: Combines multiple facts to derive an answer (e.g., "What is the population of the city where [event] occurred?")
            Provide a clear classification with reasoning.""",
            context=""
        )

        # Step 2: Extract entities and facts from documents
        entities = await self.generate(
            instruction=f"""Based on the classification: {classification}
            Extract all named entities and key facts from the question and documents.
            Focus on entities that are likely to connect documents (e.g., names, dates, locations).
            Format as a structured list with categories:
            - Entities: [list of entities]
            - Facts: [list of relevant sentences or paragraphs]""",
            context=classification
        )

        # Step 3: Build reasoning chains
        reasoning_chains = []
        entity_list = re.findall(r'\b\w+\b', entities)
        for entity in entity_list:
            chain = await self.generate(
                instruction=f"""For the entity '{entity}', construct a reasoning chain by connecting relevant facts across documents.
                Ensure each link in the chain is supported by evidence from the documents.
                Format as a sequence of connected facts leading to a potential answer.""",
                context=entities
            )
            reasoning_chains.append(chain)

        # Step 4: Synthesize and validate answers
        synthesized_answer = await self.ensemble(
            instruction="""Evaluate the reasoning chains and synthesize the most accurate answer.
            Ensure the answer is factually correct and directly supported by the documents.
            If multiple answers are plausible, prioritize the one with the strongest evidence.""",
            contexts_list=reasoning_chains
        )

        # Step 5: Iterative refinement (if needed)
        refined_answer = synthesized_answer
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the answer: {refined_answer}
                Check for consistency, factual accuracy, and completeness.
                Identify any errors or ambiguities.""",
                context=refined_answer
            )
            if "error" in validation.lower() or "ambiguous" in validation.lower():
                refined_answer = await self.revise(
                    instruction=f"""Revise the answer to address issues: {validation}
                    Ensure the revised answer is precise and well-supported.""",
                    context=refined_answer
                )
            else:
                break

        return refined_answer