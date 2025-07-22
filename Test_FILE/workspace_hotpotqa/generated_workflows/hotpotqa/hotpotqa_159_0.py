# Workflow ID: hotpotqa_159_0
# Benchmark: hotpotqa
# Data Indices: [3377, 3999, 269, 3268, 391]

<node id="1" type="input">
        <prompt>Understand the question and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the main subject and relevant context for the question. Think step by step to isolate the correct entity or event.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Search for connections between the extracted entities and known facts in the provided context. Prioritize direct matches or logical inferences.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Validate the candidate answer against all relevant context. Eliminate incorrect options based on contradictions or missing evidence.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the final, verified answer based on the reasoning chain from previous steps.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>