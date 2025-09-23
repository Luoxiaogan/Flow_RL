# Workflow ID: hotpotqa_229_0
# Benchmark: hotpotqa
# Data Indices: [442]

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

        # Initial Analysis: Identify question type and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Determine if the question is a bridge, comparison, or compositional type
            - Extract key entities, relationships, and target answer format
            - Identify potential bridge entities that connect documents""",
            context=""
        )

        # Classify Question Type
        question_type = await self.generate(
            instruction=f"""Based on the following analysis:
            {initial_analysis}
            
            Classify the question into one of these categories:
            1. Bridge: Requires connecting documents through shared entities
            2. Comparison: Involves comparing properties across documents
            3. Compositional: Needs combining multiple facts to derive the answer
            
            Provide clear classification and reasoning.""",
            context=initial_analysis
        )

        # Conditional Branching Based on Question Type
        if "bridge" in question_type.lower():
            # Parallel Fork: Find bridge entities and verify connections
            bridge_entities_tasks = [
                self.generate(
                    instruction=f"""From Document {i+1}:
                    Extract entities related to the question.
                    Focus on proper nouns, dates, and specific terms that appear in other documents.
                    List entities with their contexts.""",
                    context=""
                ) for i in range(10)  # Assuming up to 10 documents
            ]
            bridge_entities_results = await asyncio.gather(*bridge_entities_tasks)
            
            # Ensemble to Identify Best Bridge Entities
            best_bridges = await self.ensemble(
                instruction="""Identify the most promising bridge entities that connect multiple documents.
                Criteria:
                - Frequency across documents
                - Relevance to the question
                - Clarity of connection""",
                contexts_list=bridge_entities_results
            )
            
            # Build Reasoning Chain Using Identified Bridges
            reasoning_chain = await self.generate(
                instruction=f"""Using the following bridge entities:
                {best_bridges}
                
                Construct a reasoning chain that connects the documents to answer the question.
                Ensure each step is factually supported and logically follows from the previous one.""",
                context=best_bridges
            )
            
            # Extract Precise Answer
            final_answer = await self.generate(
                instruction=f"""Based on the reasoning chain:
                {reasoning_chain}
                
                Extract the precise answer span directly from the text.
                Ensure it matches the required answer format and is factually accurate.""",
                context=reasoning_chain
            )
        
        elif "comparison" in question_type.lower():
            # Parallel Fork: Extract comparable properties from each document
            properties_tasks = [
                self.generate(
                    instruction=f"""From Document {i+1}:
                    Extract properties relevant to the comparison question.
                    Focus on attributes like dates, locations, achievements, etc.
                    Provide extracted properties with their contexts.""",
                    context=""
                ) for i in range(10)
            ]
            properties_results = await asyncio.gather(*properties_tasks)
            
            # Ensemble to Compare Properties
            comparison_result = await self.ensemble(
                instruction="""Compare the extracted properties across documents.
                Determine which entity satisfies the comparison criteria.
                Provide clear justification for the conclusion.""",
                contexts_list=properties_results
            )
            
            final_answer = comparison_result
        
        else:  # Compositional Questions
            # Hierarchical Decomposition: Break down into sub-problems
            sub_problems = await self.generate(
                instruction=f"""Given the compositional nature of the question:
                {question_type}
                
                Decompose the problem into sub-problems that can be addressed individually.
                For each sub-problem, specify required information and target answer format.""",
                context=question_type
            )
            
            # Parallel Processing of Sub-Problems
            sub_solutions_tasks = [
                self.generate(
                    instruction=f"""Solve the following sub-problem:
                    {sub_prob}
                    
                    Extract necessary facts and derive the answer.""",
                    context=""
                ) for sub_prob in sub_problems.split('\n') if sub_prob.strip()
            ]
            sub_solutions = await asyncio.gather(*sub_solutions_tasks)
            
            # Ensemble to Synthesize Final Answer
            final_answer = await self.ensemble(
                instruction="""Synthesize the sub-solutions into a cohesive final answer.
                Ensure all components are integrated logically and factually.
                Present the answer in the required format.""",
                contexts_list=sub_solutions
            )
        
        # Final Refinement and Validation
        refined_answer = await self.revise(
            instruction="""Review the final answer for:
            - Factual accuracy
            - Precision in answer span extraction
            - Compliance with required format
            Make necessary improvements.""",
            context=final_answer
        )
        
        return refined_answer