# Workflow ID: hotpotqa_146_0
# Benchmark: hotpotqa
# Data Indices: [452, 336]

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

        # Phase 1: Problem Decomposition
        analysis = await self.generate(
            instruction="""Analyze the question:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities (names, dates, properties).
            3. Identify constraints or specific requirements.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Information Synthesis
        # Extract entities and constraints from analysis
        entities = await self.generate(
            instruction=f"""From the analysis:
            {analysis}
            
            Extract all key entities and constraints as a structured list.""",
            context=analysis
        )

        # Search each document for mentions of key entities
        document_search_tasks = []
        for i in range(1, 11):  # Assuming up to 10 documents
            task = self.generate(
                instruction=f"""Search Document {i} for mentions of the following entities:
                {entities}
                
                Extract relevant sentences and their context.""",
                context=""
            )
            document_search_tasks.append(task)

        document_results = await asyncio.gather(*document_search_tasks)

        # Merge findings and identify bridge entities
        merged_findings = await self.ensemble(
            instruction=f"""Merge findings from all documents:
            {document_results}
            
            Identify bridge entities that connect documents and construct a reasoning chain.""",
            contexts_list=document_results
        )

        # Phase 3: Answer Validation and Extraction
        # Extract the precise answer span
        answer_span = await self.generate(
            instruction=f"""From the reasoning chain:
            {merged_findings}
            
            Extract the precise answer span that directly answers the question.""",
            context=merged_findings
        )

        # Validate the answer
        validated_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            {answer_span}
            
            Ensure it aligns with the question and supporting facts from the reasoning chain.""",
            context=merged_findings
        )

        # Summarize the reasoning chain and answer
        final_output = await self.summarize(
            instruction=f"""Summarize the reasoning chain and validated answer:
            Reasoning Chain: {merged_findings}
            Validated Answer: {validated_answer}
            
            Provide a concise summary.""",
            context=f"{merged_findings}\n{validated_answer}"
        )

        return final_output