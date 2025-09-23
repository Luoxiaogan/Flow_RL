# Workflow ID: hotpotqa_190_0
# Benchmark: hotpotqa
# Data Indices: [204, 420]

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

        # Step 1: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Bridge question: Connects entities across documents.
            - Comparison question: Compares properties across documents.
            - Compositional question: Combines multiple facts to derive an answer.
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entity_extraction_tasks = []
        if "bridge" in question_type.lower():
            entity_extraction_tasks.append(
                self.generate(
                    instruction="Identify shared entities that connect documents.",
                    context=question_type
                )
            )
        elif "comparison" in question_type.lower():
            entity_extraction_tasks.append(
                self.generate(
                    instruction="Extract comparable attributes from documents.",
                    context=question_type
                )
            )
        else:  # Compositional
            entity_extraction_tasks.append(
                self.generate(
                    instruction="Extract all relevant facts and their relationships.",
                    context=question_type
                )
            )

        entities = await asyncio.gather(*entity_extraction_tasks)

        # Step 3: Synthesize evidence across documents
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize evidence across documents:
            - Build a coherent reasoning chain connecting the extracted facts.
            - Ensure the chain leads logically to the final answer.""",
            contexts_list=entities
        )

        # Step 4: Extract and validate the answer
        answer = await self.generate(
            instruction=f"""Extract the precise answer span from the reasoning chain:
            {reasoning_chain}
            
            Ensure the answer is concise, factually correct, and directly addresses the question.""",
            context=reasoning_chain
        )

        # Step 5: Revise for clarity and correctness
        final_answer = await self.revise(
            instruction="Ensure the answer is clear, precise, and supported by evidence.",
            context=answer
        )

        return final_answer