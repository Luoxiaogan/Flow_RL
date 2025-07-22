# Workflow ID: drop_670_0
# Benchmark: drop
# Data Indices: [2902, 1267, 2144, 3732]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical values and relationships in the problem statement. Break down the question into measurable components.</instruction>
    <input>1</input>
    <output>parsed_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Apply mathematical operations to compute the required difference or ratio based on the parsed data. Ensure precision in percentage calculations if needed.</instruction>
    <input>2</input>
    <output>result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the computed result aligns with the question's intent—e.g., checking whether it's a percentage difference, absolute difference, or ratio.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <param>final_answer</param>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>