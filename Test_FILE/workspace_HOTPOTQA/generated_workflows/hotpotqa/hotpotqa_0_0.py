# Workflow ID: hotpotqa_0_0
# Benchmark: hotpotqa
# Data Indices: [0]

import asyncio

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
        # Step 1: Decompose the question to understand reasoning structure
        question_analysis = await self.generate(
            instruction="""Perform deep question decomposition:
            1. Identify the expected answer type (entity, yes/no, comparative, etc.)
            2. Determine the minimum number of reasoning hops required
            3. List all named entities that must be connected
            4. Propose potential bridge concepts or properties (e.g., 'nationality', 'founding date', 'economic value')
            5. Flag any ambiguous terms that need disambiguation
            6. Predict which document types might contain relevant evidence
            Output in structured JSON-like format with clear section headers.""",
            context=""
        )

        # Step 2: Parallel extraction from all documents
        # Extract document texts from problem (assuming they're separated by "Document X:" pattern)
        import re
        doc_pattern = r"Document \d+: [^\n]+\n([^\n]*(?:\n[^\n]*)*)"
        document_texts = re.findall(doc_pattern, self.problem_text)
        
        # Create extraction tasks for each document
        extraction_tasks = []
        for i, doc_text in enumerate(document_texts):
            task = self.generate(
                instruction=f"""Extract ALL relevant facts from Document {i+1} that could support answering the question.
                Focus on:
                - Explicit mentions of entities from the question analysis
                - Quantitative data, comparisons, or value judgments
                - Properties that could serve as bridge concepts (dates, locations, categories, economic data)
                - Any statements that directly or indirectly relate to the target answer type
                CRITICAL: Do NOT infer or assume. Only extract verbatim phrases or clearly stated facts.
                If no relevant facts exist, output exactly: "NO_RELEVANT_FACTS"
                Prefix your output with "DOC{i+1}:" for traceability.""",
                context=doc_text
            )
            extraction_tasks.append(task)
        
        # Execute all extractions in parallel
        extracted_facts = await asyncio.gather(*extraction_tasks)
        
        # Step 3: Synthesize reasoning chains using Ensemble
        reasoning_synthesis = await self.ensemble(
            instruction="""You are a multi-hop reasoning engine. Your task:
            1. From the extracted facts, construct ALL possible reasoning chains that connect the question's entities.
            2. For each chain, explicitly state:
               - The sequence of documents used (e.g., Doc1 → Doc4)
               - The bridge concepts employed
               - The logical inference steps
               - The derived answer
            3. Rate each chain's confidence (High/Medium/Low) based on:
               - Directness of evidence
               - Number of assumptions required
               - Consistency across documents
            4. If no valid chain exists, output "INSUFFICIENT_EVIDENCE"
            5. Format output with clear chain numbering and confidence ratings.""",
            contexts_list=extracted_facts
        )

        # Step 4: Adversarial revision to stress-test the reasoning
        refined_reasoning = await self.revise(
            instruction="""Adopt an adversarial stance. Critically attack the reasoning synthesis:
            1. Identify any hidden assumptions or logical leaps
            2. Check for overlooked documents or alternative interpretations
            3. Consider edge cases (e.g., ambiguous terms, conflicting evidence)
            4. Reconstruct the strongest possible argument incorporating these critiques
            5. If the original conclusion is undermined, propose alternative answers or admit uncertainty
            Output should be a refined, more robust version of the reasoning with explicit acknowledgment of limitations.""",
            context=reasoning_synthesis
        )

        # Step 5: Precision answer extraction
        final_answer = await self.generate(
            instruction="""Extract the exact answer span as required:
            - If comparative (e.g., "which is larger"), output the winning entity name exactly as it appears in source text
            - If entity-based, output the precise phrase from the document (no paraphrasing)
            - If yes/no, output exactly "yes" or "no"
            - If insufficient evidence, output "unknown"
            Base extraction SOLELY on the refined reasoning. Do not add, infer, or modify.
            Answer must be a short text span (1-5 words max).""",
            context=refined_reasoning
        )

        return final_answer.strip()