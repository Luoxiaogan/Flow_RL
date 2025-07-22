# Workflow ID: drop_292_0
# Benchmark: drop
# Data Indices: [3797, 2115, 2625, 1073, 2804]

<node id="start" type="input">
    <param name="problem" type="string"/>
  </node>
  
  <node id="agent1" type="agent">
    <instruction>Think step by step to analyze the problem and extract relevant numerical or chronological data.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  
  <node id="agent2" type="agent">
    <instruction>Identify the key comparison or calculation required based on the extracted data. If multiple comparisons exist, prioritize the one most directly tied to the question.</instruction>
    <input>extracted_data</input>
    <output>comparison_result</output>
  </node>
  
  <node id="agent3" type="agent">
    <instruction>Verify the correctness of the comparison result by cross-checking against the passage for any ambiguous or conflicting details.</instruction>
    <input>comparison_result</input>
    <output>verified_result</output>
  </node>
  
  <node id="agent4" type="agent">
    <instruction>Format the final answer as a concise string that directly answers the original question, using only the verified result.</instruction>
    <input>verified_result</input>
    <output>final_answer</output>
  </node>
  
  <node id="end" type="output">
    <param name="answer" type="string"/>
    <input>final_answer</input>
  </node>
  
  <edge from="start" to="agent1"/>
  <edge from="agent1" to="agent2"/>
  <edge from="agent2" to="agent3"/>
  <edge from="agent3" to="agent4"/>
  <edge from="agent4" to="end"/>