# Workflow ID: drop_524_0
# Benchmark: drop
# Data Indices: [2929, 1764, 428, 3455]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>Identify the key entities and values in the passage relevant to the question. Focus on numerical data and specific terms that directly answer the query.</instruction>
    <input>1</input>
    <output>processed_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Extract all field goal distances mentioned in the passage. Determine which player corresponds to each distance, and identify the second longest one based on this list.</instruction>
    <input>2</input>
    <output>field_goal_list</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Sort the field goals in descending order of length. Select the second item from the sorted list to determine the second longest field goal.</instruction>
    <input>3</input>
    <output>sorted_field_goals</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>From the second longest field goal, retrieve the name of the player who scored it. Ensure the result is a single, clear answer without ambiguity.</instruction>
    <input>4</input>
    <output>final_answer</output>
  </node>
  
  <node id="6" type="output">
    <input>5</input>
    <param name="answer">final_answer</param>
  </node>