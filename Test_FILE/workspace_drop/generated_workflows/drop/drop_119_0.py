# Workflow ID: drop_119_0
# Benchmark: drop
# Data Indices: [3912, 1379, 598, 2647, 2142]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical values and relationships in the passage relevant to the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Extract and isolate the specific data needed to compute the answer, ensuring no irrelevant information is included.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Perform the necessary arithmetic or logical operations based on the extracted data to derive the final answer.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <connects_to>4</connects_to>
    </node>