# Workflow ID: drop_652_0
# Benchmark: drop
# Data Indices: [2046, 1302, 602, 3196]

<node id="1" type="input">
        <prompt>Understand the question and extract key information.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify relevant data points from the passage that relate to the question.</prompt>
    </node>
    <node id="3" type="process">
        <prompt>Compare or calculate based on the extracted data to answer the question.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the final answer clearly and concisely.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>