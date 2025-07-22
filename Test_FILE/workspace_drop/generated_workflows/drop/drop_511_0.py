# Workflow ID: drop_511_0
# Benchmark: drop
# Data Indices: [969, 1388, 1347, 1290, 837]

<node id="1">
    <task>Extract relevant numerical data from the passage based on the question.</task>
    <input>problem</input>
    <output>filtered_data</output>
  </node>
  <node id="2">
    <task>Identify the specific event or statistic requested in the question.</task>
    <input>filtered_data</input>
    <output>target_event</output>
  </node>
  <node id="3">
    <task>Perform arithmetic or logical operation to compute the final answer.</task>
    <input>target_event</input>
    <output>final_answer</output>
  </node>
  <node id="4">
    <task>Validate the computed result against the context of the passage.</task>
    <input>final_answer, problem</input>
    <output>validated_result</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>