# Workflow ID: drop_231_0
# Benchmark: drop
# Data Indices: [1177, 3536, 3334, 2794]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key numerical or categorical data relevant to the question. Think step by step: first, determine what is being asked, then locate the corresponding value in the passage.</instruction>
    <input>1</input>
  </node>
  
  <node id="3" type="agent">
    <instruction>Extract and validate the specific piece of information that answers the question. Ensure it aligns with the context—e.g., for a field goal, confirm yardage; for a household, confirm percentage or category.</instruction>
    <input>2</input>
  </node>
  
  <node id="4" type="agent">
    <instruction>Verify if multiple values exist in the passage that could be candidates for the answer. If so, compare them to find the correct one based on the question’s specificity (e.g., "longest", "most common").</instruction>
    <input>3</input>
  </node>
  
  <node id="5" type="output">
    <instruction>Return the final answer as a single value or label derived from the previous steps. Do not include any explanation or extra text.</instruction>
    <input>4</input>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>