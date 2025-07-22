# Workflow ID: drop_512_0
# Benchmark: drop
# Data Indices: [578, 2085, 1129, 1565]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the relevant numerical values from the passage that correspond to the question. Break down the passage step by step to extract only the necessary data points.</instruction>
        <input>1</input>
        <output>2</output>
    </node>
    <node id="3" type="agent">
        <instruction>Compare the extracted values to determine the correct answer based on the question's requirement. Ensure that you are solving for exactly what is asked — no more, no less.</instruction>
        <input>2</input>
        <output>3</output>
    </node>
    <node id="4" type="output">
        <input>3</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>