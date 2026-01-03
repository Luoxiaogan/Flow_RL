# Workflow ID: hotpotqa_111_0
# Benchmark: hotpotqa
# Data Indices: [250, 117]

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
            instruction="""Classify the question into one of the following types:
            1. Bridge Question: Requires connecting entities across documents.
            2. Comparison Question: Requires comparing properties across documents.
            3. Compositional Question: Requires combining multiple facts to derive the answer.
            Provide a clear classification and justification.""",
            context=""
        )

        # Step 2: Extract relevant information from documents
        document_tasks = []
        for i in range(10):  # Assuming up to 10 documents
            document_tasks.append(
                self.generate(
                    instruction=f"""Extract relevant information from Document {i+1} based on the question type:
                    - For Bridge Questions: Identify shared entities and relationships.
                    - For Comparison Questions: Extract comparable attributes.
                    - For Compositional Questions: Focus on key facts and their connections.
                    Format the output as structured data.""",
                    context=question_type
                )
            )
        document_info = await asyncio.gather(*document_tasks)

        # Step 3: Build reasoning chains
        reasoning_chain = await self.ensemble(
            instruction="""Synthesize information from multiple documents to build a reasoning chain:
            - For Bridge Questions: Identify the bridge entity and follow the chain to the final answer.
            - For Comparison Questions: Compare the extracted attributes to determine the correct answer.
            - For Compositional Questions: Combine multiple facts to derive the answer.
            Select the most plausible reasoning chain.""",
            contexts_list=document_info
        )

        # Step 4: Extract the final answer
        final_answer = await self.summarize(
            instruction="Condense the reasoning chain into a concise answer. Ensure the answer is factually correct and matches the expected format.",
            context=reasoning_chain
        )

        # Step 5: Validate and refine the answer (optional iterative loop)
        for _ in range(3):  # Up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the final answer. Check for factual correctness and consistency with the reasoning chain.",
                context=final_answer
            )
            if "error" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=final_answer
                )
            else:
                break

        return final_answer