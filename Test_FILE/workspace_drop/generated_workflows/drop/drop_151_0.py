# Workflow ID: drop_151_0
# Benchmark: drop
# Data Indices: [2116, 3640, 825, 1008]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage. Identify all percentages provided and note which category is being asked about.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the percentage of people who are not Pacific Islander by subtracting the Pacific Islander percentage from 100%.</instruction>
    <input>2</input>
    <output>result_percentage</output>
  </node>
  <node id="4" type="output">
    <input>3</input>
    <output>final_answer</output>
  </node>