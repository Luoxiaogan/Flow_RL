# Workflow ID: hotpotqa_515_0
# Benchmark: hotpotqa
# Data Indices: [2745, 1776, 1013, 1534, 685]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the question. Focus on direct matches or clear connections between entities.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further synthesis.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>If needed, combine multiple pieces of evidence from different context snippets to form a complete answer.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on synthesized information. Ensure clarity and correctness.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>