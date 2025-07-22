# Workflow ID: drop_244_0
# Benchmark: drop
# Data Indices: [1687, 2446, 2633, 2016]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant information from the passage related to the question. Identify key entities and numerical values mentioned.</instruction>
    <input>1</input>
    <output>extracted_info</output>
  </node>
  <node id="3" type="agent">
    <instruction>Process the extracted information step by step to determine the answer based on the question's requirements.</instruction>
    <input>2</input>
    <output>processed_answer</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the logic of the processed answer against the original passage to ensure accuracy and consistency.</instruction>
    <input>3</input>
    <output>verified_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>