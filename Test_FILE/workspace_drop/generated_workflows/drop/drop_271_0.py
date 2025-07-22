# Workflow ID: drop_271_0
# Benchmark: drop
# Data Indices: [821, 1740, 2809, 692]

<node id="1" type="input">
    <param name="problem" type="string"/>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    <param name="question" type="string"/>
    <param name="passage" type="string"/>
    <output>extracted_value</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Verify that the extracted value matches the expected format (e.g., integer for counts, float for distances).</instruction>
    <param name="value" type="any"/>
    <output>is_valid</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Check if the value corresponds to a valid answer in context (e.g., field goals in a specific quarter).</instruction>
    <param name="value" type="any"/>
    <param name="context" type="string"/>
    <output>is_contextually_correct</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Combine validation results and return final answer if all checks pass.</instruction>
    <param name="is_valid" type="boolean"/>
    <param name="is_contextually_correct" type="boolean"/>
    <param name="extracted_value" type="any"/>
    <output>final_answer</output>
  </node>
  
  <node id="6" type="output">
    <param name="answer" type="any"/>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="5"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>