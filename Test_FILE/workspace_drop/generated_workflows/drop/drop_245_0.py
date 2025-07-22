# Workflow ID: drop_245_0
# Benchmark: drop
# Data Indices: [915, 1739, 3945, 2693]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements: what is being asked, and what information is needed to answer it?</prompt>
  </node>
  
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage that relates to the question. Focus only on the values directly tied to the comparison or count in the question.</prompt>
  </node>
  
  <node id="3" type="agent">
    <prompt>Perform the necessary arithmetic operation (e.g., subtraction, comparison) based on the extracted values to find the difference or count.</prompt>
  </node>
  
  <node id="4" type="agent">
    <prompt>Verify the result by cross-checking with the original passage to ensure accuracy and relevance to the question.</prompt>
  </node>
  
  <node id="5" type="output">
    <prompt>Return the final computed answer clearly and concisely, ensuring it directly addresses the question.</prompt>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>