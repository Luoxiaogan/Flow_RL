# Workflow ID: drop_382_0
# Benchmark: drop
# Data Indices: [2845, 2111, 199, 2694]

<node id="1" type="input">
    <instruction>Receive the problem and passage as input.</instruction>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key question in the problem. Focus only on what is being asked, ignoring irrelevant details.</instruction>
  </node>
  
  <node id="3" type="agent">
    <instruction>Scan the passage for specific numerical values or events related to the question. Look for keywords like "yards", "field goal", "touchdown", etc.</instruction>
  </node>
  
  <node id="4" type="agent">
    <instruction>Determine if the relevant information is explicit (e.g., a number mentioned directly) or requires inference from context (e.g., identifying which play corresponds to the event).</instruction>
  </node>
  
  <node id="5" type="agent">
    <instruction>Extract the exact value or event that answers the question. If multiple instances exist, identify the correct one based on timing or context.</instruction>
  </node>
  
  <node id="6" type="output">
    <instruction>Return the final answer as a single numerical value or string that directly responds to the question.</instruction>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>