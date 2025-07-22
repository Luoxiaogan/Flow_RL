# Workflow ID: drop_656_0
# Benchmark: drop
# Data Indices: [1319, 823, 1691, 3889]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage. Identify all values related to the question being asked.</instruction>
    <input>1</input>
  </node>
  
  <node id="3" type="agent">
    <instruction>Compare the values to determine the difference or relationship required by the question. Focus on the key numbers that answer the specific query.</instruction>
    <input>2</input>
  </node>
  
  <node id="4" type="agent">
    <instruction>Verify the calculation step-by-step to ensure accuracy. Double-check the arithmetic and context of the values used.</instruction>
    <input>3</input>
  </node>
  
  <node id="5" type="output">
    <instruction>Return the final computed answer based on verified results from previous steps.</instruction>
    <input>4</input>
  </node>