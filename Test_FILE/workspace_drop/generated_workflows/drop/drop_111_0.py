# Workflow ID: drop_111_0
# Benchmark: drop
# Data Indices: [480, 3776, 724, 201, 3873]

<node id="start">
    <instruction>Begin processing the input problem by identifying the key question and relevant information in the passage.</instruction>
  </node>
  
  <node id="extract">
    <instruction>Extract numerical data and contextual details directly related to the question from the passage.</instruction>
    <edge to="analyze"/>
  </node>
  
  <node id="analyze">
    <instruction>Process the extracted data to determine the exact value or answer required by the question.</instruction>
    <edge to="validate"/>
  </node>
  
  <node id="validate">
    <instruction>Verify that the answer logically follows from the passage and matches the question's requirements.</instruction>
    <edge to="output"/>
  </node>
  
  <node id="output">
    <instruction>Return the final answer as a single numeric value, ensuring it is correct and unambiguous.</instruction>
  </node>
  
  <edge from="start" to="extract"/>
  <edge from="extract" to="analyze"/>
  <edge from="analyze" to="validate"/>
  <edge from="validate" to="output"/>