# Workflow ID: drop_756_0
# Benchmark: drop
# Data Indices: [3327, 1054, 2762, 1460, 1415]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract numerical values and relevant context from the passage related to the question.</instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific value or comparison needed to answer the question based on extracted data.</instruction>
        <input>extracted_data</input>
        <output>calculated_value</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify that the calculated value matches the question's requirement and is correctly derived from the passage.</instruction>
        <input>calculated_value</input>
        <output>verification_result</output>
    </node>
    
    <node id="5" type="output">
        <input>verification_result</input>
        <output>final_answer</output>
    </node>