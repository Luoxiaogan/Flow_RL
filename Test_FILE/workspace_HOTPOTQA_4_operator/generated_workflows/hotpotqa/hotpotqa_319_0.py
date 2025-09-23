# Workflow ID: hotpotqa_319_0
# Benchmark: hotpotqa
# Data Indices: [155, 471]

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

        # Step 1: Initial Analysis - Classify question type and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the question and context documents:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities mentioned in the question.
            3. Hypothesize potential bridge entities that connect documents.
            Provide structured output with clear labels.""",
            context=""
        )

        # Extract entities and question type
        entities_match = re.findall(r"Entities:\s*(.+)", initial_analysis, re.IGNORECASE)
        entities = entities_match[0].split(", ") if entities_match else []
        question_type_match = re.search(r"Question Type:\s*(\w+)", initial_analysis, re.IGNORECASE)
        question_type = question_type_match.group(1).lower() if question_type_match else "unknown"

        # Step 2: Parallel Document Processing - Extract relevant facts
        document_facts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Extract facts related to these entities: {', '.join(entities)}.
                Focus on information that connects to other documents.
                Format as bullet points.""",
                context=document
            ) for document in re.findall(r"Document \d+:[\s\S]+?(?=Document \d+:|$)", self.problem_text)]
        )

        # Step 3: Reasoning Chain Construction - Synthesize facts into a chain
        reasoning_chain = await self.ensemble(
            instruction=f"""Construct a reasoning chain using these facts:
            Facts: {' '.join(document_facts)}
            Question Type: {question_type}
            Entities: {', '.join(entities)}
            Build a logical chain that connects the facts across documents.""",
            contexts_list=document_facts
        )

        # Step 4: Answer Extraction and Validation - Extract precise answer
        answer_extraction = await self.generate(
            instruction=f"""Extract the precise answer from the reasoning chain:
            Reasoning Chain: {reasoning_chain}
            Ensure the answer is a short factual span from the text.""",
            context=reasoning_chain
        )

        # Validate and refine the answer
        refined_answer = await self.revise(
            instruction=f"""Validate the extracted answer:
            Answer: {answer_extraction}
            Ensure it is factually correct, directly supported by the documents, and matches the required format.""",
            context=answer_extraction
        )

        return refined_answer.strip()