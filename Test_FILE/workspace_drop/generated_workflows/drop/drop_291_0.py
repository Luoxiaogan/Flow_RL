# Workflow ID: drop_291_0
# Benchmark: drop
# Data Indices: [575, 3253, 3867, 467, 182]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key scoring elements in the passage relevant to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  
  <node id="3" type="agent">
    <instruction>Extract numerical data (points, field goals, touchdowns) from the passage based on the question's focus.</instruction>
    <depends_on>2</depends_on>
  </node>
  
  <node id="4" type="agent">
    <instruction>Calculate the required value by comparing or summing extracted values (e.g., total points, difference in scores).</instruction>
    <depends_on>3</depends_on>
  </node>
  
  <node id="5" type="output">
    <instruction>Return the final calculated answer as a single integer or string.</instruction>
    <depends_on>4</depends_on>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>