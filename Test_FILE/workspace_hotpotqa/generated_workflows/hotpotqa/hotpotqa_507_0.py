# Workflow ID: hotpotqa_507_0
# Benchmark: hotpotqa
# Data Indices: [2311, 2893, 2076, 570, 1631]

<operator id="1" type="agent">
        <instruction>Identify the key entities in the question and their relationships to the context.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>
    
    <operator id="2" type="agent">
        <instruction>Extract relevant information from the context that directly answers the question.</instruction>
        <input>entity_analysis, context</input>
        <output>retrieved_info</output>
    </operator>
    
    <operator id="3" type="agent">
        <instruction>Verify if the retrieved information matches the specific query about the championship group.</instruction>
        <input>retrieved_info</input>
        <output>verification</output>
    </operator>
    
    <operator id="4" type="agent">
        <instruction>Formulate a precise answer based on verified information.</instruction>
        <input>verification</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="5" type="agent">
        <instruction>Ensure the final answer is concise and only includes the required information without redundancy.</instruction>
        <input>final_answer</input>
        <output>optimized_answer</output>
    </operator>
    
    <operator id="6" type="agent">
        <instruction>Validate the output format to ensure it meets the expected structure for this problem type.</instruction>
        <input>optimized_answer</input>
        <output>output_format_validation</output>
    </operator>
    
    <operator id="7" type="agent">
        <instruction>Check for any missing or incorrect logical steps in the chain of reasoning.</instruction>
        <input>output_format_validation</input>
        <output>logical_consistency_check</output>
    </operator>
    
    <operator id="8" type="agent">
        <instruction>Return the final validated answer as the solution.</instruction>
        <input>logical_consistency_check</input>
        <output>solution</output>
    </operator>