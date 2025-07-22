# Workflow ID: drop_625_0
# Benchmark: drop
# Data Indices: [1310, 1989, 1552, 2118]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical or percentage data relevant to the question. Extract only the necessary values from the passage.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Apply the appropriate mathematical operation (e.g., subtraction, comparison, ratio) based on the question's requirement using the extracted data.</instruction>
    <input>2</input>
    <output>computed_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the computed result logically answers the question and aligns with the context of the passage.</instruction>
    <input>3</input>
    <output>verified_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>