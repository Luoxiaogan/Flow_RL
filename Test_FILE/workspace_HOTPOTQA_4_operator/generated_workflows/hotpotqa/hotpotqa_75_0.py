# Workflow ID: hotpotqa_75_0
# Benchmark: hotpotqa
# Data Indices: [283, 15]

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
            instruction="""Analyze the question and classify its type:
            1. Is it a bridge question, comparison question, or compositional question?
            2. Identify key entities, concepts, or properties mentioned in the question.
            3. Provide a structured classification and list of extracted elements.""",
            context=""
        )

        # Step 2: Parallel Exploration - Identify Bridge Entities or Relevant Properties
        bridge_entities = await self.generate(
            instruction=f"""Based on the classification and extracted elements:
            {initial_analysis}
            
            Identify potential bridge entities or relevant properties:
            - For bridge questions, list entities that connect documents.
            - For comparison questions, extract properties to compare.
            - For compositional questions, generate multiple reasoning paths.""",
            context=initial_analysis
        )

        # Parallel Search for Bridge Entities in Documents
        search_tasks = [
            self.generate(
                instruction=f"""Search for the bridge entity '{entity}' in the documents.
                Identify sentences or paragraphs where it appears.
                Extract supporting facts related to this entity.""",
                context=bridge_entities
            ) for entity in bridge_entities.split("\n") if entity.strip()
        ]
        search_results = await asyncio.gather(*search_tasks)

        # Step 3: Reasoning Chain Construction - Connect Documents and Build Chain
        reasoning_chain = await self.generate(
            instruction=f"""Using the search results:
            {search_results}
            
            Construct a reasoning chain that connects the documents:
            - Trace the logical connections between facts.
            - Ensure the chain is explicit and verifiable.
            - Summarize key facts and their relationships.""",
            context="\n".join(search_results)
        )

        # Step 4: Answer Extraction and Validation - Extract Precise Answer
        answer_extraction = await self.generate(
            instruction=f"""From the reasoning chain:
            {reasoning_chain}
            
            Extract the precise answer span from the text.
            Ensure the answer is factually correct and supported by evidence.""",
            context=reasoning_chain
        )

        # Validate and Revise Answer if Necessary
        validation = await self.generate(
            instruction=f"""Validate the extracted answer:
            {answer_extraction}
            
            Check if it is supported by the documents.
            If not, suggest revisions or alternative answers.""",
            context=answer_extraction
        )

        if "error" in validation.lower() or "uncertain" in validation.lower():
            revised_answer = await self.revise(
                instruction=f"""Revise the answer based on validation feedback:
                {validation}
                
                Ensure the final answer is precise and supported by evidence.""",
                context=answer_extraction
            )
            return revised_answer
        else:
            return answer_extraction