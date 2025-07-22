# Workflow ID: hotpotqa_301_0
# Benchmark: hotpotqa
# Data Indices: [3107, 1006, 2829, 3975, 2961]

<node id="1" type="input">
        <prompt>Understand the problem and extract key information.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the main subject and relevant context for the question. Think step by step to determine what is being asked.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Match the extracted information with known facts from the provided context. Use logical reasoning to narrow down possibilities.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the match against all available data points. Ensure no contradictions exist in your reasoning path.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Generate the final answer based on confirmed evidence from previous steps. Double-check that it directly addresses the question.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the correct answer derived from the graph execution.</prompt>
    </node>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>