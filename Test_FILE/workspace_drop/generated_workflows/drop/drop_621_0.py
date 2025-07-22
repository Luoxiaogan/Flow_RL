# Workflow ID: drop_621_0
# Benchmark: drop
# Data Indices: [71, 1327, 1038, 1606, 1562]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question. Identify key entities and values directly related to the query.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Validate the extracted data against the question's requirements. Ensure the answer is a single, clear value that directly responds to the query.</instruction>
    <input>2</input>
    <output>validated_answer</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Check for any contextual clues or alternative interpretations that might affect the final answer. Confirm no ambiguity remains.</instruction>
    <input>3</input>
    <output>final_verification</output>
  </node>
  
  <node id="5" type="output">
    <input>4</input>
    <output>answer</output>
  </node>