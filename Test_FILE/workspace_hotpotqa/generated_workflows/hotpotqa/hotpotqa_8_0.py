# Workflow ID: hotpotqa_8_0
# Benchmark: hotpotqa
# Data Indices: [2219, 2955, 3341, 2338, 2970]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the main subject and its category in the context.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>Extract relevant details from the context that directly answer the question.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>Verify if the extracted information matches the query's requirements.</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="agent">
        <prompt>Formulate a concise, accurate response based on verified data.</prompt>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <prompt>Return the final answer.</prompt>
        <depends_on>5</depends_on>
    </node>