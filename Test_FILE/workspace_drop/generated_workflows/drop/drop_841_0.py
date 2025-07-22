# Workflow ID: drop_841_0
# Benchmark: drop
# Data Indices: [1872, 3128, 851, 2994, 1647]

<node id="1" type="input">
    <prompt>Understand the question and identify relevant information from the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract numerical data directly related to the question, such as scores, counts, or statistics.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Perform necessary calculations (e.g., summing points, counting events, or deriving values).</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer based on the processed data.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>