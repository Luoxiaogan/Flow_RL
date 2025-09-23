# Workflow ID: hotpotqa_184_0
# Benchmark: hotpotqa
# Data Indices: [323]

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
        
        # Step 1: Initial Analysis (Parallel Fork)
        classification_task = self.generate(
            instruction="""Classify the question type:
            1. Bridge Question: Requires connecting documents through shared entities.
            2. Comparison Question: Involves comparing properties across documents.
            3. Compositional Question: Combines multiple facts to derive an answer.
            Provide clear classification and reasoning.""",
            context=""
        )
        
        entity_extraction_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - Entities: [names, places, organizations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]""",
            context=""
        )
        
        # Run tasks in parallel
        classification, entities = await asyncio.gather(classification_task, entity_extraction_task)
        
        # Step 2: Entity Bridging and Document Linking (Sequential Chain)
        reasoning_chain = await self.generate(
            instruction=f"""Based on the question type ({classification}) and extracted entities ({entities}):
            1. Identify bridge entities that connect documents.
            2. Construct a reasoning chain by linking documents through these entities.
            3. Highlight supporting facts for each step in the chain.""",
            context=f"{classification}

{entities}"
        )
        
        # Step 3: Reasoning and Answer Extraction (Sequential Chain)
        answer_extraction = await self.generate(
            instruction=f"""Follow the reasoning chain ({reasoning_chain}) to extract the precise answer:
            1. Identify the exact phrase or entity that answers the question.
            2. Validate the answer against supporting facts.
            3. Ensure the answer format matches the expected output (short text span or yes/no).""",
            context=reasoning_chain
        )
        
        # Step 4: Refinement and Validation (Iterative Loop)
        refined_answer = answer_extraction
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the answer ({refined_answer}):
                1. Is it factually correct?
                2. Are supporting facts sufficient?
                3. Does it meet the required format?""",
                context=refined_answer
            )
            if "error" in validation.lower() or "ambiguous" in validation.lower():
                refined_answer = await self.revise(
                    instruction=f"""Refine the answer based on validation feedback ({validation}):
                    1. Clarify ambiguous points.
                    2. Expand context if necessary.
                    3. Re-extract the precise answer.""",
                    context=refined_answer
                )
            else:
                break
        
        return refined_answer