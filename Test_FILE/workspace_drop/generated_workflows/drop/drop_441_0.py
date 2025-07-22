# Workflow ID: drop_441_0
# Benchmark: drop
# Data Indices: [2497, 1889, 2038, 1490]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values needed to answer the question based on the extracted data.</instruction>
    <input>2</input>
    <output>identified_values</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary arithmetic or logical operations using the identified values to derive the answer.</instruction>
    <input>3</input>
    <output>calculated_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>