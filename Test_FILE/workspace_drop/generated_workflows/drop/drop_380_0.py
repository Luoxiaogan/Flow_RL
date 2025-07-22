# Workflow ID: drop_380_0
# Benchmark: drop
# Data Indices: [584, 350, 2128, 3503, 185]

<node id="start" type="input">
    <param name="problem" type="string"/>
  </node>
  
  <node id="analyze_question" type="agent">
    <instruction>Identify the key elements in the question that require extraction from the passage. Focus on specific values, events, or relationships mentioned.</instruction>
  </node>
  
  <node id="locate_information" type="agent">
    <instruction>Scan the passage to find sentences that directly address the question. Extract only the relevant details without adding assumptions.</instruction>
  </node>
  
  <node id="validate_extraction" type="agent">
    <instruction>Check if the extracted information matches the question's requirements exactly. If not, re-examine the passage for more precise data.</instruction>
  </node>
  
  <node id="format_output" type="agent">
    <instruction>Structure the final answer clearly and concisely based on the validated extraction. Ensure it directly answers the question without extra details.</instruction>
  </node>
  
  <node id="end" type="output">
    <param name="answer" type="string"/>
  </node>

  <!-- Edges -->
  <edge from="start" to="analyze_question"/>
  <edge from="analyze_question" to="locate_information"/>
  <edge from="locate_information" to="validate_extraction"/>
  <edge from="validate_extraction" to="format_output"/>
  <edge from="format_output" to="end"/>