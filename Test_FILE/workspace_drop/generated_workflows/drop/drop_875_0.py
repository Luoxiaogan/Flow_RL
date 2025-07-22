# Workflow ID: drop_875_0
# Benchmark: drop
# Data Indices: [2460, 3615, 2470, 1373, 1785]

<node id="1" type="input">
    <prompt>Extract the relevant numerical data from the passage related to the question.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify all scoring plays and their respective yardages in the specified quarter. Focus only on field goals if the question asks about them.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Determine the shortest yardage among the identified field goals in that quarter.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the yardage of the shortest field goal as an integer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>