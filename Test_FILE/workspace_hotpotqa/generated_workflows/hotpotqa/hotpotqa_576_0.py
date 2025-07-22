# Workflow ID: hotpotqa_576_0
# Benchmark: hotpotqa
# Data Indices: [3449, 3799, 25, 1571, 3234]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the relevant context that contains the answer to the question.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>Extract specific details from the context that directly relate to the question.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>Verify the extracted information against the question to ensure accuracy.</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <prompt>Provide the final answer based on verified information.</prompt>
        <depends_on>4</depends_on>
    </node>