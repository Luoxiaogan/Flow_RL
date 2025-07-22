# Workflow ID: drop_57_0
# Benchmark: drop
# Data Indices: [1999, 2026, 1861, 1123, 3187]

<node id="start">
    <instruction>Begin processing the input problem. Identify the key question and relevant information in the passage.</instruction>
  </node>
  
  <node id="analyze">
    <instruction>Extract and isolate the specific data needed to answer the question. Focus only on facts directly related to the query.</instruction>
  </node>
  
  <node id="validate">
    <instruction>Verify that the extracted information is accurate, complete, and sufficient to derive a single correct answer.</instruction>
  </node>
  
  <node id="reason">
    <instruction>Use logical reasoning to connect the validated data to the question. If multiple options exist, eliminate incorrect ones based on evidence.</instruction>
  </node>
  
  <node id="output">
    <instruction>Generate the final answer as a concise, clear response based on the reasoned conclusion.</instruction>
  </node>
  
  <edge from="start" to="analyze"/>
  <edge from="analyze" to="validate"/>
  <edge from="validate" to="reason"/>
  <edge from="reason" to="output"/>