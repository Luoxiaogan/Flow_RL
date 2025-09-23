# Workflow ID: hotpotqa_90_0
# Benchmark: hotpotqa
# Data Indices: [169, 11]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Classify the question type (bridge, comparison, compositional).
            2. Extract key entities and their relationships.
            3. Identify potential bridge entities or properties.
            Provide structured classification and entity mapping.""",
            context=""
        )

        # Step 2: Parallel Exploration
        entity_linking, property_comparison, reasoning_chain = await asyncio.gather(
            self.generate(
                instruction=f"""For each entity in {analysis}, find its presence in multiple documents.
                Extract relevant sentences and document titles.
                Format as: Entity -> Document Titles -> Sentences.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""If the question involves comparison, extract comparable properties from {analysis}.
                Include units, dates, or other relevant details.
                Format as: Property -> Value -> Source Document.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Build reasoning chains based on {analysis}.
                Connect entities and properties across documents.
                Format as: Entity/Property -> Link -> Supporting Fact.""",
                context=analysis
            )
        )

        # Step 3: Conditional Branching
        if "bridge" in analysis.lower():
            refined_chain = await self.revise(
                instruction="Refine the reasoning chain by connecting entities through shared links.",
                context=reasoning_chain
            )
        elif "comparison" in analysis.lower():
            refined_chain = await self.revise(
                instruction="Compare extracted properties and determine the answer.",
                context=property_comparison
            )
        else:
            refined_chain = await self.revise(
                instruction="Combine multiple facts to derive the compositional answer.",
                context=reasoning_chain
            )

        # Step 4: Ensemble Synthesis
        final_answer = await self.ensemble(
            instruction="Synthesize all reasoning chains into the most robust answer supported by evidence.",
            contexts_list=[entity_linking, property_comparison, refined_chain]
        )

        # Step 5: Iterative Refinement
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"Validate the final answer: {final_answer}. Identify gaps or inconsistencies.",
                context=final_answer
            )
            if "gap" in validation.lower() or "inconsistent" in validation.lower():
                final_answer = await self.revise(
                    instruction=f"Refine the answer based on validation feedback: {validation}.",
                    context=final_answer
                )
            else:
                break

        return final_answer