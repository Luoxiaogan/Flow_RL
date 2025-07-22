# Workflow ID: hotpotqa_158_0
# Benchmark: hotpotqa
# Data Indices: [1437, 1751, 3719, 3133, 2642]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities in the context that relate to the question. Focus on the national park mentioned, its founding year, and the species Agnorisma bolli.</instruction>
        <input>1</input>
        <output>3</output>
    </node>
    <node id="3" type="agent">
        <instruction>From the identified entities, determine which national park was chartered in 1934 and is known to host Agnorisma bolli.</instruction>
        <input>2</input>
        <output>4</output>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the selected national park matches both the charter year (1934) and the presence of Agnorisma bolli based on the provided context.</instruction>
        <input>3</input>
        <output>5</output>
    </node>
    <node id="5" type="agent">
        <instruction>Return the name of the national park that satisfies both conditions: established in 1934 and contains Agnorisma bolli.</instruction>
        <input>4</input>
        <output>6</output>
    </node>
    <node id="6" type="output">
        <data>result</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>