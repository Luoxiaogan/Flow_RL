# Workflow ID: drop_599_0
# Benchmark: drop
# Data Indices: [3772, 1465, 3147, 2603]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical data relevant to the question. Extract all instances of field goals and their details from the passage.</instruction>
        <input>1</input>
        <output>field_goal_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>From the extracted field goal data, determine which kicker is associated with each field goal and count how many field goals each kicker made.</instruction>
        <input>2</input>
        <output>kicker_field_goals</output>
    </node>
    <node id="4" type="agent">
        <instruction>Identify the kicker named "Gostkowski" in the list of kickers and retrieve the number of field goals he made.</instruction>
        <input>3</input>
        <output>gostkowski_field_goals</output>
    </node>
    <node id="5" type="output">
        <instruction>Return the number of field goals made by Gostkowski as the final answer.</instruction>
        <input>4</input>
        <output>final_answer</output>
    </node>