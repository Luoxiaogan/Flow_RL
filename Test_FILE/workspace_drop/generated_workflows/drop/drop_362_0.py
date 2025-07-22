# Workflow ID: drop_362_0
# Benchmark: drop
# Data Indices: [2990, 1792, 2214, 1495, 3755]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract key numerical data from the passage relevant to the question. Identify scores, yardages, and time periods mentioned.</instruction>
    <input>problem</input>
    <output>key_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Parse the question to determine what is being asked—e.g., difference in scores, number of touchdowns, etc.</instruction>
    <input>problem</input>
    <output>query_type</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Apply mathematical or logical operations based on query_type and key_data to compute the answer.</instruction>
    <input>
      <data>key_data</data>
      <type>query_type</type>
    </input>
    <output>computed_answer</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Verify that the computed answer aligns with the context of the passage and matches the expected format (e.g., integer for counts, difference for yardage).</instruction>
    <input>
      <answer>computed_answer</answer>
      <context>problem</context>
    </input>
    <output>final_answer</output>
  </node>
  
  <node id="6" type="output">
    <input>final_answer</input>
  </node>
  
  <edge from="1" to="2" />
  <edge from="1" to="3" />
  <edge from="2" to="4" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />
  <edge from="5" to="6" />