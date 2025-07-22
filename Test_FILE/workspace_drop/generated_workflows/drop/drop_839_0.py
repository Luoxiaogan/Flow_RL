# Workflow ID: drop_839_0
# Benchmark: drop
# Data Indices: [2248, 3686, 1970, 702]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Identify the key variables and relationships needed to solve the problem step by step.</instruction>
    <input>2</input>
    <output>variables_and_relations</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Apply mathematical or logical operations based on the identified variables to compute the answer.</instruction>
    <input>3</input>
    <output>computed_answer</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Verify the computed answer against the original context to ensure accuracy.</instruction>
    <input>4</input>
    <output>verified_answer</output>
  </node>
  
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>