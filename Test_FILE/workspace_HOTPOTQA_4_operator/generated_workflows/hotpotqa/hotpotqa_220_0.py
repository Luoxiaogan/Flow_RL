# Workflow ID: hotpotqa_220_0
# Benchmark: hotpotqa
# Data Indices: [372, 476]

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

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the question and context documents:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities, relationships, and constraints.
            3. Highlight potential bridge entities linking documents.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Parallel Document Analysis
        document_analysis_tasks = [
            self.generate(
                instruction=f"""Analyze this document for relevant information:
                - Identify key facts and entities.
                - Highlight connections to other documents.
                - Focus on the question and bridge entities.""",
                context=document
            )
            for document in self.problem_text.split("**CONTEXT DOCUMENTS:**")[1].split("**QUESTION:**")[0].split("Document ")[1:]
        ]
        document_analyses = await asyncio.gather(*document_analysis_tasks)

        # Phase 3: Entity Linking and Reasoning
        bridge_entities = await self.ensemble(
            instruction="""Identify bridge entities connecting documents:
            - Find shared entities or relationships.
            - Prioritize entities most relevant to the question.
            - Resolve ambiguities by cross-referencing documents.""",
            contexts_list=document_analyses
        )

        reasoning_strategy = await self.generate(
            instruction=f"""Based on the identified bridge entities ({bridge_entities}), determine the reasoning strategy:
            - For bridge questions, trace the chain of linked entities.
            - For comparison questions, compare properties across documents.
            - For compositional questions, combine multiple facts.
            Provide a clear plan.""",
            context=analysis
        )

        # Phase 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer span or yes/no response:
            - Follow the reasoning strategy ({reasoning_strategy}).
            - Use only information from the provided documents.
            - Ensure the answer is factually correct and supported by evidence.""",
            context=bridge_entities
        )

        validated_answer = await self.revise(
            instruction="""Validate the extracted answer:
            - Check for factual correctness.
            - Ensure precision and clarity.
            - Refine the output if necessary.""",
            context=answer_extraction
        )

        return validated_answer