# Workflow ID: hotpotqa_388_0
# Benchmark: hotpotqa
# Data Indices: [824, 3860, 3407, 137]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context for each entity mentioned in the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further processing.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Apply logical reasoning to connect entities and derive the final answer.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the correct answer based on processed information.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>