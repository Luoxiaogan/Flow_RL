# Workflow ID: hotpotqa_33_0
# Benchmark: hotpotqa
# Data Indices: [793, 2032, 1060, 3179]

<operator id="0" type="agent">
        <instruction>Identify the key elements in the question and determine the relevant context to solve it.</instruction>
        <input>problem</input>
        <output>step1_output</output>
    </operator>
    
    <operator id="1" type="agent">
        <instruction>Extract the specific information from the context that directly answers the question.</instruction>
        <input>step1_output</input>
        <output>step2_output</output>
    </operator>
    
    <operator id="2" type="agent">
        <instruction>Verify that the extracted information is accurate and fully addresses the question.</instruction>
        <input>step2_output</input>
        <output>step3_output</output>
    </operator>
    
    <operator id="3" type="agent">
        <instruction>Formulate a clear, concise final answer based on the verified information.</instruction>
        <input>step3_output</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="4" type="agent">
        <instruction>Double-check the logic flow and ensure no steps were skipped or misinterpreted.</instruction>
        <input>final_answer</input>
        <output>verification_result</output>
    </operator>
    
    <operator id="5" type="agent">
        <instruction>Ensure all operators contribute meaningfully to the final output without redundancy.</instruction>
        <input>verification_result</input>
        <output>optimized_graph</output>
    </operator>