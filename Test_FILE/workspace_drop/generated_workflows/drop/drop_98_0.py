# Workflow ID: drop_98_0
# Benchmark: drop
# Data Indices: [462, 1873, 1106, 1311]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the percentage of households with children under 18 and the percentage of households with someone living alone who is 65 or older.</instruction>
        <output>percent_children, percent_senior</output>
    </node>
    <node id="3" type="agent">
        <instruction>Calculate the difference in percentages between households with children under 18 and those with seniors living alone.</instruction>
        <output>difference_percent</output>
    </node>
    <node id="4" type="agent">
        <instruction>Determine the percentage increase from the senior-alone group to the children-under-18 group using the formula: ((children - senior) / senior) * 100.</instruction>
        <output>percent_increase</output>
    </node>
    <node id="5" type="output">
        <data>percent_increase</data>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>