# Workflow ID: drop_573_0
# Benchmark: drop
# Data Indices: [3546, 34, 1127, 16, 3325]

<node id="1" type="input">
    <prompt>Extract the relevant numerical data from the passage that answers the question.</prompt>
  </node>
  
  <node id="2" type="process">
    <prompt>Identify the key values or quantities mentioned in the passage related to the question. For example, if the question asks about a difference, find both numbers involved in the comparison.</prompt>
  </node>
  
  <node id="3" type="process">
    <prompt>Apply mathematical operations (e.g., subtraction, addition) based on the question's requirement to compute the final answer.</prompt>
  </node>
  
  <node id="4" type="output">
    <prompt>Return the computed result as the answer to the question.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>