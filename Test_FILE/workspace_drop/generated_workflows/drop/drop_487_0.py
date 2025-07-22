# Workflow ID: drop_487_0
# Benchmark: drop
# Data Indices: [3290, 464, 1126, 1981, 1300]

<node id="1" type="input">
    <prompt>Extract relevant numerical data from the passage related to field goals and touchdowns.</prompt>
  </node>
  
  <node id="2" type="process">
    <prompt>Calculate total yards for Billy Cundiff's field goals: sum of 52, 33, and 26.</prompt>
  </node>
  
  <node id="3" type="process">
    <prompt>Calculate total yards for Sebastian Janikowski's field goals: sum of 46 and 38.</prompt>
  </node>
  
  <node id="4" type="process">
    <prompt>Subtract Janikowski's total from Cundiff's total to find the difference.</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the calculated difference in field goal yards.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>