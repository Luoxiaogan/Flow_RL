# Workflow ID: drop_352_0
# Benchmark: drop
# Data Indices: [1274, 64, 1107, 613, 1157]

<node id="1" type="input">
        <description>Receive problem input</description>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant data from the passage based on the question.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Identify key numerical values or events that directly answer the question.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Perform necessary calculations or logical deductions using extracted values.</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Verify the result against the context to ensure accuracy and relevance.</instruction>
    </node>
    <node id="6" type="output">
        <description>Return the final answer based on the verified result.</description>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>