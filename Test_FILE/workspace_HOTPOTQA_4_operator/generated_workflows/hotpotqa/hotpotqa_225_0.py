# Workflow ID: hotpotqa_225_0
# Benchmark: hotpotqa
# Data Indices: [10]

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

        # Step 1: Extract entities and relationships from all documents in parallel
        async def extract_entities(doc_title):
            return await self.generate(
                instruction=f"""
                From the document titled '{doc_title}', extract:
                - Key entities (people, places, organizations)
                - Relationships between entities
                - Important facts or properties
                Format as structured JSON:
                {{
                    "entities": [...],
                    "relationships": [...],
                    "facts": [...]
                }}
                """,
                context=""
            )

        # Identify document titles dynamically
        doc_titles = []
        lines = self.problem_text.split("\n")
        for line in lines:
            if line.startswith("Document") and ":" in line:
                doc_titles.append(line.split(":")[1].strip())

        # Parallel entity extraction
        entity_results = await asyncio.gather(*[extract_entities(title) for title in doc_titles])

        # Consolidate extracted information
        consolidated_context = "\n".join(entity_results)

        # Step 2: Identify bridge entities and construct reasoning chains
        reasoning_chains = []
        for i in range(3):  # Attempt up to 3 iterations for refinement
            chain = await self.generate(
                instruction=f"""
                Using the extracted information:
                {consolidated_context}
                
                Construct a reasoning chain to answer the question:
                - Identify bridge entities that connect documents
                - Follow relationships to build a logical path
                - Ensure each step is factually supported
                Format as a step-by-step chain:
                1. [Step 1]
                2. [Step 2]
                ...
                Final Answer: [Answer]
                """,
                context=consolidated_context
            )
            # Refine the reasoning chain
            refined_chain = await self.revise(
                instruction="""
                Critique the reasoning chain:
                - Check for logical consistency
                - Ensure all steps are factually supported
                - Add missing details or clarify ambiguities
                """,
                context=chain
            )
            reasoning_chains.append(refined_chain)

            # Early termination if chain is satisfactory
            if "error" not in refined_chain.lower():
                break

        # Step 3: Evaluate and select the best reasoning chain
        best_chain = await self.ensemble(
            instruction="""
            Evaluate the reasoning chains and select the best one:
            - Logical consistency
            - Factual accuracy
            - Completeness of reasoning
            Return the selected chain.
            """,
            contexts_list=reasoning_chains
        )

        # Step 4: Extract the final answer
        final_answer = await self.generate(
            instruction=f"""
            From the selected reasoning chain:
            {best_chain}
            
            Extract the final answer:
            - Ensure it is a short text span or yes/no response
            - Verify it matches the expected answer format
            """,
            context=best_chain
        )

        return final_answer