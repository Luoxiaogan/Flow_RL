# Workflow ID: hotpotqa_548_0
# Benchmark: hotpotqa
# Data Indices: [2373, 1278, 2688, 3166, 2713]

<node id="1" type="input">
        <prompt>Understand the question and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the relevant context that links the key entities to the answer.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further inference.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>If needed, perform logical reasoning using the verified context to derive the final answer.</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answer based on the reasoning path.</prompt>
        <depends_on>4</depends_on>
    </node>