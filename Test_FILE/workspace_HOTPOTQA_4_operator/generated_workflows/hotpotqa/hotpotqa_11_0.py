# Workflow ID: hotpotqa_11_0
# Benchmark: hotpotqa
# Data Indices: [203, 24]

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
        
        # Step 1: Initial Analysis - Identify question type and key entities
        initial_analysis = await self.generate(
            instruction="""Classify the question type (bridge, comparison, compositional).
            Extract key entities and relationships mentioned in the question.
            Focus on identifying potential bridge entities that connect documents.
            Provide structured classification and extracted entities.""",
            context=""
        )
        
        # Step 2: Entity Connection Exploration - Generate hypotheses about connections
        hypotheses = await asyncio.gather(
            *[self.generate(
                instruction=f"""Explore potential connections between entities across documents.
                Based on initial analysis: {initial_analysis}.
                Hypothesize how entities might be related in the context of the question.
                Consider shared entities, comparative properties, or compositional facts.""",
                context=initial_analysis
            ) for _ in range(3)]  # Generate multiple perspectives
        )
        
        # Step 3: Hypothesis Refinement - Critique and refine each hypothesis
        refined_hypotheses = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique the hypothesis for factual accuracy and logical consistency.
                Ensure connections are valid and supported by document content.
                Refine the hypothesis accordingly.""",
                context=hypothesis
            ) for hypothesis in hypotheses]
        )
        
        # Step 4: Evidence Summarization - Summarize supporting evidence for each hypothesis
        summarized_evidence = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Summarize the supporting evidence for the refined hypothesis.
                Focus on key facts directly related to the question.
                Exclude irrelevant details.""",
                context=hypothesis
            ) for hypothesis in refined_hypotheses]
        )
        
        # Step 5: Synthesis and Decision - Combine hypotheses and select the best answer
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the refined hypotheses and their supporting evidence.
            Select the most plausible hypothesis based on factual support and logical consistency.
            If multiple hypotheses are complementary, merge them into a unified answer.
            Ensure the final answer is concise and directly addresses the question.""",
            contexts_list=summarized_evidence
        )
        
        # Step 6: Validation and Final Answer - Validate and refine the final answer
        validated_answer = await self.revise(
            instruction=f"""Validate the final answer against the original question.
            Ensure factual accuracy, logical consistency, and precision.
            Refine the answer if necessary to improve clarity or correctness.""",
            context=final_answer
        )
        
        return validated_answer