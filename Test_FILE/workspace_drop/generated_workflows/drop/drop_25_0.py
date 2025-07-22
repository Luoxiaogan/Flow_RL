# Workflow ID: drop_25_0
# Benchmark: drop
# Data Indices: [337, 1600, 390, 3807]

<node id="1" type="input">
    <prompt>Extract the relevant information from the passage to answer the question.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify all instances where Daunte Culpepper threw a touchdown pass. Sum the yardage of each pass.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Calculate the total yards from Culpepper's touchdown passes only—ignore rushing touchdowns.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the sum of all touchdown pass yardages by Daunte Culpepper.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>