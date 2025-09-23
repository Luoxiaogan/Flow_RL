# Workflow ID: hotpotqa_68_0
# Benchmark: hotpotqa
# Data Indices: [114, 231]

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
        
        # Initial Analysis: Classify question and identify key components
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Identify key entities and relationships mentioned in the question.
            Provide a structured overview of the problem.""",
            context=""
        )
        
        # Parallel Entity Extraction from each document
        entities_extraction_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            entities_extraction_tasks.append(
                self.generate(
                    instruction=f"""Extract all named entities, numbers, and relationships from Document {i+1}.
                    Focus on entities related to the question.
                    Format as structured list with categories:
                    - People: [names and roles]
                    - Places: [locations and contexts]
                    - Numbers: [values and what they represent]
                    - Actions: [what happens and when]""",
                    context=initial_analysis
                )
            )
        extracted_entities = await asyncio.gather(*entities_extraction_tasks)
        
        # Summarize extracted entities to consolidate findings
        consolidated_entities = await self.summarize(
            instruction="Consolidate extracted entities across documents.",
            context="\n".join(extracted_entities)
        )
        
        # Reasoning Chain Construction
        reasoning_chain = await self.generate(
            instruction=f"""Using the consolidated entities: {consolidated_entities}
            Build reasoning chains that connect entities across documents.
            Validate each chain against the question requirements.
            Highlight any missing links or ambiguities.""",
            context=initial_analysis
        )
        
        # Answer Synthesis
        answer_synthesis = await self.generate(
            instruction=f"""Using the reasoning chains: {reasoning_chain}
            Synthesize the final answer.
            Extract exact answer spans from the text.
            Identify supporting facts from different documents.""",
            context=consolidated_entities
        )
        
        # Final Refinement: Revise and summarize the result
        refined_answer = await self.revise(
            instruction="Ensure clarity, correctness, and completeness of the final answer.",
            context=answer_synthesis
        )
        
        final_answer = await self.summarize(
            instruction="Condense the refined answer into a short, factual response.",
            context=refined_answer
        )
        
        return final_answer