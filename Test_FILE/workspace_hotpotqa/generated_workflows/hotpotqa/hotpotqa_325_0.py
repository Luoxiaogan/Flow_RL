# Workflow ID: hotpotqa_325_0
# Benchmark: hotpotqa
# Data Indices: [3746, 97, 3319, 1480]

<node id="1" type="input">
        <prompt>Understand the question and identify key entities mentioned.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Extract relevant information from context related to the main subject (e.g., "Italian pianist and composer" in Problem 4).</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Identify which Italian pianist or composer was associated with Canzoniere Grecanico Salentino based on the context.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>From the identified pianist/composer, retrieve their birth date from the context.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the full birth date of the Italian pianist and composer who performed with Canzoniere Grecanico Salentino.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>