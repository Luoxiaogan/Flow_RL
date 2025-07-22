# Workflow ID: drop_49_0
# Benchmark: drop
# Data Indices: [540, 684, 3698, 1095]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage related to the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Process the extracted data to find the answer step-by-step.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the solution against the passage for accuracy.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on validated steps.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>