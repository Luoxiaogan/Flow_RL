# Workflow ID: drop_700_0
# Benchmark: drop
# Data Indices: [442, 1016, 3461, 3373, 2391]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the values in extracted_data to determine the answer based on the question.</instruction>
    <input>extracted_data</input>
    <output>comparison_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Format the final answer clearly and concisely based on the comparison result.</instruction>
    <input>comparison_result</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <param name="answer" value="final_answer" />
  </node>
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />