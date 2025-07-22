# Workflow ID: drop_232_0
# Benchmark: drop
# Data Indices: [2939, 596, 2857, 2332, 1004]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage. Identify the total number of people and families.</instruction>
        <input>1</input>
        <output>people_count, family_count</output>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the difference between the number of people and families by subtracting family count from people count.</instruction>
        <input>2</input>
        <output>difference</output>
    </node>
    <node id="4" type="output">
        <input>3</input>
        <result>difference</result>
    </node>