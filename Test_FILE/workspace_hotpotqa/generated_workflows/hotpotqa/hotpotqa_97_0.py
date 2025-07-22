# Workflow ID: hotpotqa_97_0
# Benchmark: hotpotqa
# Data Indices: [652, 3029, 3322, 924]

<node id="1" type="input">
        <prompt>Understand the problem and extract key entities and relationships.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the relevant information in the context that answers the question. Focus on specific dates, names, and events related to the question.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Verify if the extracted information directly answers the question or requires further processing. Check for ambiguity or missing data.</prompt>
    </node>
    <node id="4" type="operator">
        <prompt>Filter and match the data using logical conditions (e.g., birth year = 1985).</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Confirm the final answer by cross-referencing with other known facts from the context.</prompt>
    </node>
    <node id="6" type="output">
        <prompt>Return the correct answer based on the filtered and verified data.</prompt>
    </node>

    <!-- Edges -->
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>