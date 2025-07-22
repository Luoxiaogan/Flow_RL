# Workflow ID: drop_592_0
# Benchmark: drop
# Data Indices: [1242, 1717, 2211, 2704, 282]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key numerical data in the passage relevant to the question. Break down the information step by step to locate the answer.</instruction>
    <input>problem</input>
    <output>key_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Extract and organize the relevant values from the key data. Use logical reasoning to compare or calculate as needed for the specific question.</instruction>
    <input>key_data</input>
    <output>processed_data</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Apply the appropriate mathematical or logical operation to derive the final answer based on the processed data. Ensure the solution aligns with the question asked.</instruction>
    <input>processed_data</input>
    <output>final_answer</output>
  </node>
  
  <node id="5" type="output">
    <input>final_answer</input>
  </node>
  
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />