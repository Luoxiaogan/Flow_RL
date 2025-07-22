# Workflow ID: hotpotqa_344_0
# Benchmark: hotpotqa
# Data Indices: [3204, 1417, 3641, 2466, 3024]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from the context related to the question.</prompt>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <prompt>Verify the extracted information for accuracy and relevance.</prompt>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <prompt>Identify the specific detail needed to answer the question (e.g., birth year).</prompt>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="agent">
        <prompt>Formulate the final answer based on the verified data.</prompt>
        <depends_on>4</depends_on>
    </node>
    <node id="6" type="output">
        <prompt>Return the correct answer.</prompt>
        <depends_on>5</depends_on>
    </node>