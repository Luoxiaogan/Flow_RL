# Workflow ID: drop_224_0
# Benchmark: drop
# Data Indices: [535, 2749, 3541, 2149, 3597]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all values that could be part of the answer.</instruction>
    <input>1</input>
    <output>extracted_values</output>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the extracted values to determine which group has the smaller percentage based on the question's criteria.</instruction>
    <input>2</input>
    <output>comparison_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Format the final answer as a percentage value with appropriate precision, ensuring it directly answers the question.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <data>final_answer</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>