# Workflow ID: drop_319_0
# Benchmark: drop
# Data Indices: [267, 1547, 1277, 349]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or values to compare.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage related to the question. Focus on values that can be compared directly.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted values step-by-step to determine which is greater or if they are equal.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the comparison aligns with the context of the question (e.g., longest field goal, income difference, etc.).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the comparison result.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>