# Workflow ID: hotpotqa_8_0
# Benchmark: hotpotqa
# Data Indices: [409]

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
            1. Is it a bridge question (connecting entities across documents)?
            2. Is it a comparison question (evaluating properties of entities)?
            3. Is it a compositional question (combining multiple facts)?
            Provide a clear classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships
        entities = await self.generate(
            instruction=f"""Extract all named entities, relationships, and key phrases from the context documents:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Question Type: {question_type}""",
            context=""
        )

        # Step 3: Build reasoning chains (parallel exploration)
        reasoning_chains = await asyncio.gather(
            self.generate(
                instruction=f"""Construct reasoning chain for entities: {entities}
                Follow logical connections across documents.
                Focus on entities relevant to the question type: {question_type}.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Explore alternative reasoning chains for entities: {entities}
                Consider secondary connections and less direct relationships.""",
                context=entities
            )
        )

        # Step 4: Select the best reasoning chain
        selected_chain = await self.ensemble(
            instruction=f"""Evaluate and select the most promising reasoning chain:
            Criteria:
            - Logical consistency
            - Factual accuracy
            - Relevance to the question type: {question_type}
            
            Candidate Chains: {reasoning_chains}""",
            contexts_list=reasoning_chains
        )

        # Step 5: Extract the precise answer
        answer = await self.generate(
            instruction=f"""Extract the exact answer span from the selected reasoning chain:
            Chain: {selected_chain}
            Ensure the answer is factually correct and directly addresses the question.""",
            context=selected_chain
        )

        # Step 6: Validate and refine (iterative loop)
        max_iterations = 3
        for _ in range(max_iterations):
            validation = await self.revise(
                instruction=f"""Validate the answer: {answer}
                Check against the reasoning chain: {selected_chain}
                Identify any inconsistencies or missing details.""",
                context=answer
            )
            if "error" not in validation.lower():
                break
            answer = await self.revise(
                instruction=f"""Revise the answer based on validation feedback: {validation}
                Improve clarity and correctness.""",
                context=answer
            )

        return answer