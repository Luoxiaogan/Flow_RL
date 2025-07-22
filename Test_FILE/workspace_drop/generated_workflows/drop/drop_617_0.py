# Workflow ID: drop_617_0
# Benchmark: drop
# Data Indices: [3528, 1502, 1542, 2400, 3566]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question. Identify key entities, events, and values that directly answer the query.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Perform step-by-step reasoning based on extracted data. Determine the necessary calculations or logical comparisons to arrive at the correct answer.</instruction>
        <input>2</input>
        <output>reasoning_result</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify the correctness of the reasoning by cross-checking against the original passage. Ensure no critical detail is missed or misinterpreted.</instruction>
        <input>3</input>
        <output>verification_result</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>