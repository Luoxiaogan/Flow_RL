# Workflow ID: hotpotqa_492_0
# Benchmark: hotpotqa
# Data Indices: [2820, 2233, 514, 1932, 3877]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the main subject and relevant context from the question.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>Match the subject to known individuals or events in the provided context.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the match by cross-referencing details such as achievements, roles, or affiliations.</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="agent">
        <prompt>Ensure all criteria from the question are satisfied by the candidate answer.</prompt>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <prompt>Return the final answer that satisfies all conditions of the question.</prompt>
        <depends_on>5</depends_on>
    </node>