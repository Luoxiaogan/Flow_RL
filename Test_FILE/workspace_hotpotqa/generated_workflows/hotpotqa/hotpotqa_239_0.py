# Workflow ID: hotpotqa_239_0
# Benchmark: hotpotqa
# Data Indices: [513, 3158, 2477, 358, 191]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant context related to the key entities. Focus on direct connections between the entities and the answer.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify that the extracted information directly answers the question without ambiguity.</prompt>
    </node>
    <node id="4" type="validator">
        <prompt>Check if the answer is unambiguous and supported by the context.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final, validated answer.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>