# Workflow ID: drop_465_0
# Benchmark: drop
# Data Indices: [2829, 548, 2276, 436, 1832]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify all relevant numerical data related to the question.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract the yardage of Brady's touchdown pass to Faulk and to Jabar Gaffney from the passage.</prompt>
  </node>
  <node id="3" type="process">
    <prompt>Calculate the difference in yards between the two touchdown passes.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the numerical difference in yards as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>