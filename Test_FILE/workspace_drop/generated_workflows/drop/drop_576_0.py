# Workflow ID: drop_576_0
# Benchmark: drop
# Data Indices: [3150, 1514, 2649, 173, 631]

<node id="1" type="input">
    <prompt>Understand the question and identify the key data needed to solve it.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant numerical or categorical values from the passage that relate to the question.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Perform the necessary calculation or comparison based on the extracted data.</prompt>
  </node>
  <node id="4" type="validate">
    <prompt>Verify the calculation or logic is correct and matches the question's requirement.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in the required format (e.g., percentage, difference, etc.).</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>