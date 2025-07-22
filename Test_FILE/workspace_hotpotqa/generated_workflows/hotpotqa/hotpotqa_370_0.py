# Workflow ID: hotpotqa_370_0
# Benchmark: hotpotqa
# Data Indices: [2482, 739, 2933, 1840, 1127]

<node id="1" type="input">
        <prompt>Understand the problem statement and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant context information related to the key entities. Focus on direct connections between entities and the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Validate each extracted piece of information against the question's requirements. Eliminate irrelevant or ambiguous data.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Identify the correct answer by matching validated information with the specific query.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the matched information from node 4.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>