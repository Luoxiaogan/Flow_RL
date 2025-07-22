# Workflow ID: hotpotqa_16_0
# Benchmark: hotpotqa
# Data Indices: [2217, 2952, 3684, 2657, 2027]

<node id="1" type="input">
        <prompt>Understand the question and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify relevant information from context for each entity. Focus on dates or age indicators.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Compare the birth years of both individuals to determine who is younger.</prompt>
    </node>
    <node id="4" type="output">
        <prompt>Return the name of the younger musician based on the comparison.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>