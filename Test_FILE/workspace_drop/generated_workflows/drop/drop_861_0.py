# Workflow ID: drop_861_0
# Benchmark: drop
# Data Indices: [2525, 3301, 2601, 1386]

<node id="start" type="input">
    <instruction>Extract relevant dates from the passage for the two events mentioned in the question.</instruction>
  </node>
  
  <node id="date1" type="operator">
    <instruction>Identify the year of the first establishment (Russia).</instruction>
  </node>
  
  <node id="date2" type="operator">
    <instruction>Identify the year of the second establishment (Italy).</instruction>
  </node>
  
  <node id="calculate" type="operator">
    <instruction>Subtract the first year from the second year to get the difference in years.</instruction>
  </node>
  
  <node id="result" type="output">
    <instruction>Return the number of full years between the two establishments.</instruction>
  </node>

  <!-- Edges -->
  <edge from="start" to="date1"/>
  <edge from="start" to="date2"/>
  <edge from="date1" to="calculate"/>
  <edge from="date2" to="calculate"/>
  <edge from="calculate" to="result"/>