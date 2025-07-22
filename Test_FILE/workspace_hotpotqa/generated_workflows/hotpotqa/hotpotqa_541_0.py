# Workflow ID: hotpotqa_541_0
# Benchmark: hotpotqa
# Data Indices: [2800, 230, 1569, 3971]

<node id="1" type="input">
    <prompt>Receive problem input</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify key entities and relationships in the context to extract relevant information for the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Apply reasoning to connect extracted facts with the question's requirements, focusing on one specific answer per step.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the solution aligns with all provided context clues and does not introduce unsupported assumptions.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final, verified answer based on logical inference from the context.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>