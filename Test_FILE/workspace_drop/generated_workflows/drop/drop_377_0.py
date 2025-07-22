# Workflow ID: drop_377_0
# Benchmark: drop
# Data Indices: [942, 717, 1322, 2147]

<node id="1" type="input">
    <prompt>Understand the question and identify key numerical values needed to solve it.</prompt>
  </node>
  
  <node id="2" type="process">
    <prompt>Extract relevant data from the passage that pertains to the question. Focus only on the numbers or events mentioned in relation to the query.</prompt>
  </node>
  
  <node id="3" type="process">
    <prompt>Apply the correct mathematical operation (e.g., subtraction, comparison) based on the question's requirement.</prompt>
  </node>
  
  <node id="4" type="validate">
    <prompt>Check if the calculated result aligns with the context of the passage — no unrealistic values (e.g., negative yards for a field goal).</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the final answer as a single integer value derived from the steps above.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>