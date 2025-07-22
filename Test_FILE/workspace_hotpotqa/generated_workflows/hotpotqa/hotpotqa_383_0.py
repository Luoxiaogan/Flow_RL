# Workflow ID: hotpotqa_383_0
# Benchmark: hotpotqa
# Data Indices: [3007, 481, 3736, 2716]

<node id="1" type="input">
        <prompt>Understand the question and identify key elements to solve it.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context that directly relates to the question. Focus on precise details without overgeneralizing.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information provides a clear answer or requires further reasoning based on logical connections.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>If the answer is not immediately available, infer relationships between concepts in the context to deduce the correct response.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Ensure all steps logically lead to a single coherent conclusion. Eliminate any conflicting interpretations.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the final answer based on the validated chain of reasoning.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>