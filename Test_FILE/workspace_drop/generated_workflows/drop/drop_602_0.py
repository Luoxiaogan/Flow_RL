# Workflow ID: drop_602_0
# Benchmark: drop
# Data Indices: [2544, 264, 1614, 2409, 291]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Identify the specific values needed to answer the question based on the extracted data.</instruction>
    <input>2</input>
    <output>identified_values</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Perform the necessary calculation using the identified values.</instruction>
    <input>3</input>
    <output>calculation_result</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Verify that the calculation is correct and matches the context of the question.</instruction>
    <input>4</input>
    <output>verification_result</output>
  </node>
  
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>