# Workflow ID: hotpotqa_444_0
# Benchmark: hotpotqa
# Data Indices: [1774, 3756, 152, 1339, 126]

<agent name="QuestionAnalyzer">
        <instruction>Break down the question to identify key entities and relationships. Focus on what is being asked and what information is needed to answer it.</instruction>
    </agent>
    
    <agent name="ContextExtractor">
        <instruction>From the provided context, extract all relevant information related to the entities mentioned in the question. Prioritize clarity and relevance to avoid noise.</instruction>
    </agent>
    
    <agent name="Reasoner">
        <instruction>Use logical reasoning to connect extracted facts. Determine if direct comparison, timeline analysis, or contextual inference is required to answer the question.</instruction>
    </agent>
    
    <agent name="Validator">
        <instruction>Verify that the answer logically follows from the reasoning step. Check for consistency with known facts and eliminate contradictions or ambiguities.</instruction>
    </agent>
    
    <agent name="AnswerGenerator">
        <instruction>Formulate a clear, concise answer based on validated reasoning. Ensure the response directly addresses the original question without unnecessary elaboration.</instruction>
    </agent>
    
    <edge from="QuestionAnalyzer" to="ContextExtractor"/>
    <edge from="ContextExtractor" to="Reasoner"/>
    <edge from="Reasoner" to="Validator"/>
    <edge from="Validator" to="AnswerGenerator"/>