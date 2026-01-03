# Workflow ID: hotpotqa_32_0
# Benchmark: hotpotqa
# Data Indices: [80]

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
            - Bridge: Requires connecting entities across documents (e.g., "What nationality is the director of [movie]?")
            - Comparison: Requires comparing properties across documents (e.g., "Which was founded first, X or Y?")
            - Compositional: Requires combining multiple facts to derive the answer
            Provide the classification and reasoning.""",
            context=""
        )

        # Step 2: Extract entities and relationships from all documents
        entity_tasks = [
            self.generate(
                instruction=f"""Extract key entities and relationships from the following document:
                {doc}
                Format as a structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            )
            for doc in self.extract_documents()
        ]
        entities_list = await asyncio.gather(*entity_tasks)
        entities_summary = await self.summarize(
            instruction="Condense the extracted entities into a unified list.",
            context="\n".join(entities_list)
        )

        # Step 3: Build reasoning chains
        reasoning_chains = []
        if "bridge" in question_type.lower():
            reasoning_chains = await self.generate(
                instruction=f"""Construct reasoning chains connecting the following entities:
                {entities_summary}
                Focus on shared entities that bridge documents.""",
                context=question_type
            )
        elif "comparison" in question_type.lower():
            reasoning_chains = await self.generate(
                instruction=f"""Construct reasoning chains comparing the following entities:
                {entities_summary}
                Focus on numerical or temporal data.""",
                context=question_type
            )
        else:  # Compositional
            reasoning_chains = await self.generate(
                instruction=f"""Construct reasoning chains combining the following entities:
                {entities_summary}
                Focus on multiple bridge entities.""",
                context=question_type
            )

        # Step 4: Validate and refine reasoning chains
        refined_chains = await self.revise(
            instruction="Refine the reasoning chains for clarity and logical consistency.",
            context=reasoning_chains
        )

        # Step 5: Extract the final answer
        final_answer = await self.ensemble(
            instruction="Select the most accurate and concise answer supported by the reasoning chains.",
            contexts_list=refined_chains.split("\n\n")  # Split chains into individual options
        )

        return final_answer

    def extract_documents(self):
        """Extract individual documents from the problem text."""
        # Placeholder implementation
        return ["Document 1 content", "Document 2 content", "Document 3 content"]