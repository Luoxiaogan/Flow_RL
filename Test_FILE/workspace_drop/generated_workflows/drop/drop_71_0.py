# Workflow ID: drop_71_0
# Benchmark: drop
# Data Indices: [3222, 3409, 375, 3490, 1023]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points in the passage relevant to the question.</instruction>
        <depends_on>1</depends_on>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the required percentage or value based on the extracted data, ensuring all steps are logically connected.</instruction>
        <depends_on>2</depends_on>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the calculation aligns with the question's requirement and check for any missing or misinterpreted information.</instruction>
        <depends_on>3</depends_on>
    </node>
    <node id="5" type="output">
        <data>final_answer</data>
        <depends_on>4</depends_on>
    </node>