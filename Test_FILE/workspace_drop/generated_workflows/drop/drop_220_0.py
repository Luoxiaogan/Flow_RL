# Workflow ID: drop_220_0
# Benchmark: drop
# Data Indices: [2988, 1977, 3218, 644]

<node id="start" type="input">
    <prompt>Understand the question and identify required data from the passage.</prompt>
  </node>
  
  <node id="extract" type="agent">
    <prompt>Extract relevant numerical values related to the question. Focus on specific metrics such as distances, counts, or monetary values.</prompt>
  </node>
  
  <node id="process" type="agent">
    <prompt>Perform necessary calculations or comparisons using the extracted data. For example, subtract revenue from expenses or count items meeting a condition.</prompt>
  </node>
  
  <node id="validate" type="agent">
    <prompt>Verify that the calculation aligns with the question's requirements and that no steps were missed.</prompt>
  </node>
  
  <node id="output" type="output">
    <prompt>Return the final answer based on validated result.</prompt>
  </node>

  <!-- Edges -->
  <edge from="start" to="extract"/>
  <edge from="extract" to="process"/>
  <edge from="process" to="validate"/>
  <edge from="validate" to="output"/>