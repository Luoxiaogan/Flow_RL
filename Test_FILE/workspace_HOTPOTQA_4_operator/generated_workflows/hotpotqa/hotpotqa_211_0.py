# Workflow ID: hotpotqa_211_0
# Benchmark: hotpotqa
# Data Indices: [325]

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

        # Step 1: Identify question type and extract entities/relationships
        initial_analysis = await self.generate(
            instruction="""Analyze the question and classify it into one of three types:
            - Bridge: Requires connecting shared entities across documents.
            - Comparison: Involves comparing properties or attributes.
            - Compositional: Needs synthesis of multiple facts.
            Extract all relevant entities and relationships from the context documents.
            Format the output as:
            Question Type: [Type]
            Entities: [List of entities]
            Relationships: [List of relationships]""",
            context=""
        )

        # Step 2: Parallel exploration of reasoning chains
        entities = await self.generate(
            instruction="Extract entities mentioned in the initial analysis.",
            context=initial_analysis
        )
        relationships = await self.generate(
            instruction="Extract relationships mentioned in the initial analysis.",
            context=initial_analysis
        )

        reasoning_chains = await asyncio.gather(
            *[self.generate(
                instruction=f"""Explore reasoning chain for entity: {entity}.
                Follow relationships across documents to connect information.""",
                context=relationships
            ) for entity in entities.split("\n")]
        )

        # Step 3: Conditional branching based on question type
        question_type = "Bridge"  # Extracted from initial_analysis dynamically
        if question_type == "Bridge":
            refined_chain = await self.revise(
                instruction="Refine reasoning chain to connect shared entities across documents.",
                context="\n".join(reasoning_chains)
            )
        elif question_type == "Comparison":
            refined_chain = await self.revise(
                instruction="Refine reasoning chain to compare properties across documents.",
                context="\n".join(reasoning_chains)
            )
        else:  # Compositional
            refined_chain = await self.revise(
                instruction="Refine reasoning chain to synthesize multiple facts.",
                context="\n".join(reasoning_chains)
            )

        # Step 4: Iterative refinement loop
        for _ in range(3):  # Maximum 3 iterations
            validation = await self.generate(
                instruction="Validate the reasoning chain for completeness and accuracy.",
                context=refined_chain
            )
            if "error" in validation.lower():
                refined_chain = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined_chain
                )
            else:
                break

        # Step 5: Final synthesis and answer extraction
        final_answer = await self.ensemble(
            instruction="Synthesize the refined reasoning chain into a concise answer. Ensure the answer is factually correct and supported by the documents.",
            contexts_list=[refined_chain, initial_analysis]
        )

        return final_answer