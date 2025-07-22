# Workflow ID: drop_277_0
# Benchmark: drop
# Data Indices: [2487, 986, 2074, 384, 329]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific condition or range mentioned in the question (e.g., percentage, age group, years).</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Compare the extracted values against the condition to determine the correct answer.</instruction>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that the result is consistent with the context of the problem and matches the required format.</instruction>
  </node>
  <node id="6" type="output">
    <data>final_answer</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>