# Workflow ID: drop_177_0
# Benchmark: drop
# Data Indices: [3135, 1540, 315, 3922, 2428]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key numerical information in the passage related to the question. Focus on specific statistics or counts mentioned directly.</instruction>
        <input>1</input>
        <output>key_info</output>
    </node>
    <node id="3" type="agent">
        <instruction>Extract the relevant value from the key information that answers the question. If multiple values exist, determine which one is directly tied to the query.</instruction>
        <input>2</input>
        <output>answer_value</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the extracted value matches the question's requirement and that no other interpretation of the passage yields a different answer.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
    </node>