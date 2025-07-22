# Workflow ID: drop_221_0
# Benchmark: drop
# Data Indices: [3293, 2011, 132, 1256, 3402]

<node id="1">
    <task>Identify the relevant information in the passage related to the question.</task>
    <input>problem</input>
    <output>filtered_info</output>
  </node>
  <node id="2">
    <task>Extract numerical or categorical data that directly answers the question.</task>
    <input>filtered_info</input>
    <output>extracted_data</output>
  </node>
  <node id="3">
    <task>Compare or analyze the extracted data based on the question's requirement.</task>
    <input>extracted_data</input>
    <output>analysis_result</output>
  </node>
  <node id="4">
    <task>Formulate the final answer using logical reasoning from the analysis.</task>
    <input>analysis_result</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>