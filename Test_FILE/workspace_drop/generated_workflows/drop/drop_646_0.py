# Workflow ID: drop_646_0
# Benchmark: drop
# Data Indices: [2232, 2842, 2485, 783]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify all instances where the subject of the question is mentioned in relation to the quantity being asked (e.g., field goals, touchdowns).</instruction>
    <input>2</input>
    <output>relevant_instances</output>
  </node>
  <node id="4" type="agent">
    <instruction>Sum up the values associated with each instance for the final answer.</instruction>
    <input>3</input>
    <output>summed_total</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>