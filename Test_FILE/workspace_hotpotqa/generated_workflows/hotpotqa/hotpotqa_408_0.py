# Workflow ID: hotpotqa_408_0
# Benchmark: hotpotqa
# Data Indices: [1163, 1535, 489, 3570]

<node id="1" type="input">
        <description>Receive problem context and question</description>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract key entities and dates from the context relevant to the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    
    <node id="3" type="agent">
        <instruction>Compare the extracted data to determine the correct answer by reasoning step-by-step.</instruction>
        <depends_on>2</depends_on>
    </node>
    
    <node id="4" type="agent">
        <instruction>Validate the reasoning path against all provided context to avoid contradictions.</instruction>
        <depends_on>3</depends_on>
    </node>
    
    <node id="5" type="output">
        <instruction>Return the final answer based on validated reasoning.</instruction>
        <depends_on>4</depends_on>
    </node>