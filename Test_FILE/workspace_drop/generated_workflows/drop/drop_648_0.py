# Workflow ID: drop_648_0
# Benchmark: drop
# Data Indices: [2398, 1649, 3913, 3337]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Identify the key comparison or value being asked in the question.</instruction>
    <input>2</input>
    <output>comparison_value</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Compare the two values (e.g., average household size vs. average family size) and determine which is smaller.</instruction>
    <input>3</input>
    <output>result</output>
  </node>
  
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>