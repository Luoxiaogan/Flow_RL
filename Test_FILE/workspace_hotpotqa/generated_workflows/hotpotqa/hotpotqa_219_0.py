# Workflow ID: hotpotqa_219_0
# Benchmark: hotpotqa
# Data Indices: [3690, 3883, 3884, 633, 1466]

<node id="1" type="input">
        <prompt>Understand the task and identify key elements from the context.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context for each question step by step.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>Map extracted information to answer each question logically.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>Validate answers against the context to ensure accuracy.</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <prompt>Return the final answers in a structured format.</prompt>
        <depends_on>4</depends_on>
    </node>