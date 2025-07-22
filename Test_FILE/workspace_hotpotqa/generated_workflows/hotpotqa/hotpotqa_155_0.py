# Workflow ID: hotpotqa_155_0
# Benchmark: hotpotqa
# Data Indices: [1056, 444, 1607, 1243, 3893]

<node id="1" type="input">
        <prompt>Understand the question and extract key entities.</prompt>
    </node>
    <node id="2" type="agent">
        <prompt>Identify the common profession between Muhammad Iqbal and Allen Ginsberg by analyzing their roles in the context.</prompt>
    </node>
    <node id="3" type="agent">
        <prompt>Determine the parliamentary component representing Fredericton since 1988 using electoral district information.</prompt>
    </node>
    <node id="4" type="agent">
        <prompt>Find the film starring Peter O'Toole and an English actress known for a grieving mother role, and identify the actress.</prompt>
    </node>
    <node id="5" type="agent">
        <prompt>Identify the location of the Spartakiad based on the given context about Czechoslovakia.</prompt>
    </node>
    <node id="6" type="agent">
        <prompt>Locate the city where Angelo Meli led a Mafia crime family based on the provided context.</prompt>
    </node>
    <node id="7" type="output">
        <prompt>Aggregate all answers into a final structured response.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="1" to="4"/>
    <edge from="1" to="5"/>
    <edge from="1" to="6"/>
    <edge from="2" to="7"/>
    <edge from="3" to="7"/>
    <edge from="4" to="7"/>
    <edge from="5" to="7"/>
    <edge from="6" to="7"/>