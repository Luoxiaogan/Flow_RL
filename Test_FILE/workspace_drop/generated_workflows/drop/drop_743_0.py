# Workflow ID: drop_743_0
# Benchmark: drop
# Data Indices: [3838, 2982, 3280, 2551, 481]

<node id="1" type="input">
    <prompt>Extract all field goal distances mentioned in the passage.</prompt>
    <output>list_of_distances</output>
  </node>
  
  <node id="2" type="process">
    <prompt>Identify the maximum value from the list of field goal distances.</prompt>
    <input>list_of_distances</input>
    <output>longest_field_goal</output>
  </node>
  
  <node id="3" type="output">
    <prompt>Return the longest field goal distance as the answer.</prompt>
    <input>longest_field_goal</input>
  </node>