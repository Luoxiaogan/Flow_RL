# Workflow ID: hotpotqa_535_0
# Benchmark: hotpotqa
# Data Indices: [1464, 1426, 3403, 2072]

<node id="1" type="agent">
        <instruction>Identify the key details in the question: film title, year, director, character name, and actress birth date.</instruction>
    </node>
    <node id="2" type="agent">
        <instruction>Extract the relevant information from the context: find the film "Up to His Neck", its director, and the actress who played Rakiki.</instruction>
    </node>
    <node id="3" type="agent">
        <instruction>Confirm the actress's full name and birth date by cross-referencing with other entries in the context that mention her.</instruction>
    </node>
    <node id="4" type="agent">
        <instruction>Verify that the actress born on 7 February 1922 is indeed the one who played Rakiki in "Up to His Neck".</instruction>
    </node>
    <node id="5" type="agent">
        <instruction>Return the final answer: the English comedy actress who played Rakiki in "Up to His Neck".</instruction>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>