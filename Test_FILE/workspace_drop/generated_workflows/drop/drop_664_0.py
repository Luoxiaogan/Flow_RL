# Workflow ID: drop_664_0
# Benchmark: drop
# Data Indices: [2830, 2132, 2778, 3213, 1307]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific value that answers the question based on extracted data.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Validate the answer by cross-referencing with other details in the passage if necessary.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <data>final_answer</data>
        <depends_on>4</depends_on>
    </node>