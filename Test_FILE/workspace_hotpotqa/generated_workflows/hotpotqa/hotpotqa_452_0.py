# Workflow ID: hotpotqa_452_0
# Benchmark: hotpotqa
# Data Indices: [160, 239, 3879, 3432]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem. Focus on the main subject, the action, and the context.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract all relevant data points from the context that pertain to the question. Prioritize chronological, biographical, or categorical details.</instruction>
        <input>context</input>
        <output>data_extraction</output>
    </operator>
    
    <operator id="3">
        <instruction>Verify if the extracted data directly answers the question. If not, identify missing links or infer based on known associations.</instruction>
        <input>data_extraction, entity_analysis</input>
        <output>verification_and_inference</output>
    </operator>
    
    <operator id="4">
        <instruction>Construct a concise answer by combining verified facts and logical inference. Ensure it addresses the question precisely without extra information.</instruction>
        <input>verification_and_inference</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5">
        <instruction>Validate the final answer against the original question to ensure accuracy and completeness. Check for any contradictions or ambiguities.</instruction>
        <input>final_answer, problem</input>
        <output>validation_result</output>
    </operator>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>