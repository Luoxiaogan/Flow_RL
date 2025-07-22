# Workflow ID: drop_87_0
# Benchmark: drop
# Data Indices: [2018, 448, 2995, 2884]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Extract the key numerical value from the passage that answers the question. Think step by step: identify the relevant sentence, locate the number, and verify it matches the question's context.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Validate the extracted number by cross-referencing with the passage's timeline or category. Ensure the number is not a percentage, age group, yardage, or other unrelated metric if the question asks for years, percent, yards, or time period respectively.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="output">
        <data>3</data>
        <input>3</input>
    </node>