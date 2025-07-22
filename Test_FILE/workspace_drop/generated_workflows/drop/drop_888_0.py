# Workflow ID: drop_888_0
# Benchmark: drop
# Data Indices: [2650, 372, 2688, 3057]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant percentages from the passage based on the question. Identify the key numerical data that directly answers the query.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform arithmetic operations (e.g., subtraction, percentage calculation) to derive the final answer from the extracted values. Think step by step to ensure accuracy.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="output">
    <instruction>Return the final computed percentage or value as the solution to the problem.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>