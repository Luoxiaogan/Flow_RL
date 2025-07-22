# Workflow ID: drop_545_0
# Benchmark: drop
# Data Indices: [1236, 1394, 606, 1507]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data points in the passage relevant to the question. Break down the passage step by step to locate exact values or ranges.</instruction>
    <input>1</input>
    <output>key_data_points</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter the key data points to extract only those that directly answer the question. Ignore irrelevant details such as team names, locations, or non-numeric context.</instruction>
    <input>2</input>
    <output>filtered_values</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary calculations (e.g., percentages, totals) based on filtered values to derive the final answer. Ensure all steps are logically sound and mathematically correct.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <parameter>result</parameter>
  </node>