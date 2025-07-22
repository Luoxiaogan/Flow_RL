# Workflow ID: drop_767_0
# Benchmark: drop
# Data Indices: [869, 486, 1975, 281]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key numerical or categorical data relevant to the question from the passage.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the extracted values step by step to determine which group, army, or event is larger, more numerous, or occurred first.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the comparison logic and ensure it aligns with the question's requirement—e.g., age group size, army strength, scoring in a time frame, or chronological order.</instruction>
  </node>
  <node id="5" type="agent">
    <instruction>Validate that all steps logically lead to a single definitive answer without ambiguity or contradiction.</instruction>
  </n>
  <node id="6" type="output">
    <data>final_answer</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>