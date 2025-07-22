# Workflow ID: drop_388_0
# Benchmark: drop
# Data Indices: [2050, 2001, 1813, 929, 3507]

<node id="1" type="input">
        <prompt>Read the passage carefully and identify the key information relevant to the question.</prompt>
    </node>
    
    <node id="2" type="agent">
        <prompt>Think step by step: Extract the exact answer from the passage based on the question. Do not guess or infer beyond what is stated.</prompt>
    </node>
    
    <node id="3" type="agent">
        <prompt>Verify that the extracted answer matches the question exactly. If not, recheck the passage for clarity or context.</prompt>
    </node>
    
    <node id="4" type="output">
        <prompt>Return only the final answer as a concise string. No explanation or extra text.</prompt>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>