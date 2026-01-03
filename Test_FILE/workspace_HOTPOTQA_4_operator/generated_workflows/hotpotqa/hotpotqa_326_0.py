# Workflow ID: hotpotqa_326_0
# Benchmark: hotpotqa
# Data Indices: [322, 180]

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

        # Step 1: Initial Analysis - Identify Question Type and Potential Bridge Entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (bridge, comparison) and identify potential bridge entities or comparison targets.
            - What entities are mentioned in the question?
            - Which documents contain information about these entities?
            - What is the relationship between these entities?
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Parallel Exploration - Extract Relevant Information from Multiple Documents
        entities = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Extract all relevant entities and relationships from the context documents.
            - List entities and their associated documents.
            - Identify sentences containing these entities.
            - Highlight potential bridges or comparisons.
            Format as structured list.""",
            context=initial_analysis
        )

        # Split entities into separate tasks for parallel processing
        entity_tasks = []
        for entity in entities.split('\n'):
            entity_task = self.generate(
                instruction=f"""For entity: {entity}
                - Find all related information from its associated document.
                - Extract sentences containing this entity.
                - Identify relationships and connections to other entities.
                Provide detailed findings.""",
                context=entities
            )
            entity_tasks.append(entity_task)

        entity_results = await asyncio.gather(*entity_tasks)

        # Step 3: Validation and Refinement - Critique and Improve Extracted Information
        refined_results = []
        for result in entity_results:
            refined_result = await self.revise(
                instruction=f"""Critique and improve the extracted information:
                - Ensure factual accuracy.
                - Enhance clarity and logical consistency.
                - Add missing details if necessary.
                Original Extraction: {result}""",
                context=result
            )
            refined_results.append(refined_result)

        # Step Output Compression - Summarize Key Findings
        summarized_results = []
        for refined in refined_results:
            summary = await self.summarize(
                instruction=f"""Condense the refined information:
                - Focus on key entities and relationships.
                - Preserve essential details for reasoning.
                Refined Information: {refined}""",
                context=refined
            )
            summarized_results.append(summary)

        # Step 4: Synthesis and Decision - Select Best Reasoning Chain and Extract Final Answer
        synthesis = await self.ensemble(
            instruction=f"""Synthesize the summarized findings into a coherent reasoning chain:
            - Connect entities across documents.
            - Build explicit reasoning steps.
            - Identify the final answer span directly from text.
            Summarized Results: {summarized_results}""",
            contexts_list=summarized_results
        )

        final_answer = await self.generate(
            instruction=f"""Extract the precise answer from the synthesized reasoning chain:
            - Ensure it is factually correct.
            - Match the required format (short text span or yes/no).
            - Include supporting facts from different documents.
            Synthesis: {synthesis}""",
            context=synthesis
        )

        return final_answer