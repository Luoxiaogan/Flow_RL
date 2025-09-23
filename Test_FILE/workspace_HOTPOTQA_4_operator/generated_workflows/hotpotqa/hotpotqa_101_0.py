# Workflow ID: hotpotqa_101_0
# Benchmark: hotpotqa
# Data Indices: [256]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio
        
        # Step 1: Parallel Fork for Initial Analysis
        initial_tasks = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, relationships, and key phrases that might serve as bridges between documents.
                Format them categorically:
                - People: [names, roles]
                - Organizations: [names, types]
                - Dates: [events, timelines]
                - Concepts: [definitions, contexts]""",
                context=""
            ),
            self.generate(
                instruction="""Classify the question into one of the following types: bridge, comparison, compositional.
                Provide detailed rationale for your classification.
                - Bridge: Connect documents through shared entities.
                - Comparison: Compare properties across documents.
                - Compositional: Combine multiple facts to derive an answer.""",
                context=""
            )
        )
        entities = initial_tasks[0]
        question_type_classification = initial_tasks[1]

        # Step 2: Conditional Branching Based on Question Type
        if "bridge" in question_type_classification.lower():
            # Bridge Question Workflow
            reasoning_chain = ""
            for i in range(3):  # Up to 3 iterations for refinement
                next_step = await self.generate(
                    instruction=f"""Using the identified entities: {entities}
                    And the current reasoning chain: {reasoning_chain}
                    
                    Identify the next logical connection or fact linking documents.
                    Ensure each step explicitly references document titles and sentences.""",
                    context=reasoning_chain
                )
                validation = await self.generate(
                    instruction=f"""Validate the coherence and factual accuracy of this reasoning step:
                    {next_step}""",
                    context=reasoning_chain
                )
                if "error" in validation.lower() or "inaccurate" in validation.lower():
                    next_step = await self.revise(
                        instruction=f"""Correct inaccuracies or gaps in the reasoning step based on validation feedback:
                        {validation}""",
                        context=next_step
                    )
                reasoning_chain += f"\n{next_step}"
            
            # Final Answer Extraction
            answer = await self.generate(
                instruction=f"""Based on the complete reasoning chain:
                {reasoning_chain}
                
                Extract the precise answer span from the final document.
                Include the exact sentence(s) supporting the answer.""",
                context=reasoning_chain
            )
        
        elif "comparison" in question_type_classification.lower():
            # Comparison Question Workflow
            comparison_steps = []
            attributes = await self.generate(
                instruction="Identify the specific attributes or properties being compared in the question.",
                context=""
            )
            for attribute in attributes.split('\n'):
                comparison = await self.generate(
                    instruction=f"""Compare the attribute '{attribute.strip()}' across relevant documents.
                    Present findings systematically:
                    - Document 1: [value/explanation]
                    - Document 2: [value/explanation]
                    - Conclusion: [comparison result]""",
                    context=""
                )
                comparison_steps.append(comparison)
            
            # Ensemble to Synthesize Comparison Results
            answer = await self.ensemble(
                instruction="Synthesize all comparison steps into a unified conclusion. Ensure factual accuracy and coherence.",
                contexts_list=comparison_steps
            )
        
        elif "compositional" in question_type_classification.lower():
            # Compositional Question Workflow
            compositional_steps = []
            facts = await self.generate(
                instruction="Identify all individual facts mentioned in the question that need to be combined.",
                context=""
            )
            for fact in facts.split('\n'):
                composition = await self.generate(
                    instruction=f"""Integrate the fact '{fact.strip()}' into the overall reasoning.
                    Ensure each step logically follows from previous ones and references supporting documents.""",
                    context="\n".join(compositional_steps)
                )
                compositional_steps.append(composition)
            
            # Ensemble to Synthesize Compositional Results
            answer = await self.ensemble(
                instruction="Combine all compositional steps into a coherent final answer. Maintain factual precision.",
                contexts_list=compositional_steps
            )
        
        else:
            # Default Comprehensive Approach
            answer = await self.generate(
                instruction="""Apply a general multi-hop reasoning approach:
                - Identify relevant documents and entities.
                - Build a logical reasoning chain.
                - Extract the precise answer span with supporting evidence.""",
                context=""
            )
        
        return answer