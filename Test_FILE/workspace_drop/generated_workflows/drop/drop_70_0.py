# Workflow ID: drop_70_0
# Benchmark: drop
# Data Indices: [3143, 790, 2310, 2397]

<node id="1" type="input">
    <param name="problem" type="string"/>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract all touchdown pass lengths from the passage. Focus only on pass plays, not runs or returns.</instruction>
    <param name="output" type="list"/>
  </node>
  
  <node id="3" type="agent">
    <instruction>Identify the shortest touchdown pass length from the extracted list.</instruction>
    <param name="output" type="int"/>
  </node>
  
  <node id="4" type="agent">
    <instruction>Determine which player caught the shortest touchdown pass by matching the length to the play description.</instruction>
    <param name="output" type="string"/>
  </node>
  
  <node id="5" type="agent">
    <instruction>Return the final answer as a string: "The shortest touchdown pass was [length] yards, caught by [player]."</instruction>
    <param name="output" type="string"/>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>