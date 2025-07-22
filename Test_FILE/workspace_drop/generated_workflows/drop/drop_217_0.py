# Workflow ID: drop_217_0
# Benchmark: drop
# Data Indices: [3306, 1822, 1910, 2574]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage related to the question. Focus only on the specific value being asked for.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Compare all extracted values if multiple numbers are present to determine the correct answer based on the question's requirement (e.g., highest, lowest, total).</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="output">
    <prompt>Return the final answer as a single integer or value that directly answers the question.</prompt>
    <dependencies>3</dependencies>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>