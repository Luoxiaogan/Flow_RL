# Workflow ID: drop_267_0
# Benchmark: drop
# Data Indices: [685, 2831, 3125, 1046]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the passage. Focus on the specific question being asked and extract relevant information.</instruction>
        <input>1</input>
        <output>processed_info</output>
    </node>
    <node id="3" type="agent">
        <instruction>Based on the processed information, determine the exact answer to the question by focusing only on the relevant data points.</instruction>
        <input>2</input>
        <output>answer</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify the answer by cross-checking with the original passage to ensure accuracy and completeness.</instruction>
        <input>2</input>
        <input>3</input>
        <output>verification</output>
    </node>
    <node id="5" type="output">
        <data>answer</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="2" to="4"/>
    <edge from="3" to="5"/>
    <edge from="4" to="5"/>