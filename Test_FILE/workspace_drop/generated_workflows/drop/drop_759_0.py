# Workflow ID: drop_759_0
# Benchmark: drop
# Data Indices: [3371, 2554, 3260, 2956, 3322]

<node id="1" type="input">
    <prompt>Understand the question and identify required data from the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant numerical values or quantities needed to solve the problem step by step.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Apply arithmetic operations (addition, subtraction, comparison) based on extracted values.</prompt>
  </node>
  <node id="4" type="validate">
    <prompt>Verify that the solution aligns with the context of the question and passage.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in a clear and concise format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>