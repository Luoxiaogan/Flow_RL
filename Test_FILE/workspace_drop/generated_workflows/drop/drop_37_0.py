# Workflow ID: drop_37_0
# Benchmark: drop
# Data Indices: [3565, 3105, 581, 3085]

<node id="start" type="input">
    <prompt>Understand the task and identify key elements to solve the problem.</prompt>
  </node>
  
  <node id="agent1" type="agent">
    <prompt>Break down the problem into smaller components. Identify what information is needed to answer the question.</prompt>
  </node>
  
  <node id="agent2" type="agent">
    <prompt>Locate relevant details in the passage that directly address the question. Avoid irrelevant data.</prompt>
  </node>
  
  <node id="agent3" type="agent">
    <prompt>Apply logical reasoning to connect the extracted facts. Ensure no assumptions are made beyond the text.</prompt>
  </node>
  
  <node id="agent4" type="agent">
    <prompt>Verify the solution by cross-checking against the passage for consistency and completeness.</prompt>
  </node>
  
  <node id="output" type="output">
    <prompt>Return the final, accurate answer based on the reasoning from all agents.</prompt>
  </node>
  
  <edge from="start" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="agent4"/>
  <edge from="agent4" to="output"/>