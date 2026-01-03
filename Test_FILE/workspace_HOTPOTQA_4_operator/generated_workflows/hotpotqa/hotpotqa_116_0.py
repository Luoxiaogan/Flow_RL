# Workflow ID: hotpotqa_116_0
# Benchmark: hotpotqa
# Data Indices: [352, 308]

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
        
        # Step 1: Initial Analysis - Classify Question Type and Extract Key Entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (bridge, comparison, compositional).
            2. Identify key entities mentioned in the question.
            3. Note any specific constraints or requirements for the answer.
            Provide structured output with clear labels.""",
            context=""
        )
        
        # Step 2: Parallel Document Analysis - Identify Bridge Entities and Facts
        documents = self.problem_text.split("**QUESTION:**")[0].split("Document")
        document_tasks = []
        for doc in documents[1:]:
            title, content = doc.split(":", 1)
            task = self.generate(
                instruction=f"""Analyze this document:
                Title: {title.strip()}
                Content: {content.strip()}
                
                Tasks:
                1. Identify all named entities (people, places, organizations).
                2. Extract key facts and relationships.
                3. Highlight any entities that match those in the question.
                Format as structured output.""",
                context=initial_analysis
            )
            document_tasks.append(task)
        document_results = await asyncio.gather(*document_tasks)
        
        # Step 3: Entity Linking and Reasoning Chain Construction
        entity_linking = await self.ensemble(
            instruction="""Compare the outputs from document analyses:
            1. Identify overlapping entities across documents.
            2. Construct a reasoning chain that connects these entities.
            3. Ensure the chain leads to the answer for the given question.
            Provide a clear explanation of the reasoning process.""",
            contexts_list=document_results
        )
        
        # Step 4: Answer Extraction and Validation
        answer_extraction = await self.generate(
            instruction=f"""Using the reasoning chain:
            {entity_linking}
            
            Extract the precise answer span from the relevant document(s).
            Ensure the answer is factually correct and matches the question's requirements.""",
            context=entity_linking
        )
        
        # Iterative Validation Loop
        validated_answer = answer_extraction
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction=f"""Validate the extracted answer:
                {validated_answer}
                
                Check for:
                1. Factual correctness based on the documents.
                2. Precision in matching the question's focus.
                3. Any missing details or ambiguities.
                Provide feedback for improvement if needed.""",
                context=validated_answer
            )
            if "error" not in validation.lower() and "improve" not in validation.lower():
                break
            validated_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                {validation}""",
                context=validated_answer
            )
        
        return validated_answer