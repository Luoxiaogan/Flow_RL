# Workflow ID: drop_435_0
# Benchmark: drop
# Data Indices: [56, 3819, 2129, 104]

<node id="1" type="input">
    <prompt>Understand the question and extract key numerical values from the passage.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Identify the relevant data points for comparison (e.g., ratio of males to females 18+).</prompt>
  </node>
  <node id="3" type="compute">
    <prompt>Calculate the difference in numbers per 100 females: subtract male count from female count (100 - males per 100 females).</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the calculated difference as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>