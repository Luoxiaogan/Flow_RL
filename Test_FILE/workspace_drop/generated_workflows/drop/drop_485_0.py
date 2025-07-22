# Workflow ID: drop_485_0
# Benchmark: drop
# Data Indices: [364, 852, 3521, 2176]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key numerical data and relationships from the problem statement. Identify what is being asked and what information is provided.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary arithmetic or logical operations based on the extracted data. Ensure all calculations are precise and aligned with the question.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the solution satisfies the original question. If not, re-evaluate the steps to correct any errors.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>