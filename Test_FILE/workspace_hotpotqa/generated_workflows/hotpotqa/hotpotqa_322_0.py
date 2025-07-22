# Workflow ID: hotpotqa_322_0
# Benchmark: hotpotqa
# Data Indices: [3176, 3734, 1822, 1346]

<node id="1">
    <operator>agent_1</operator>
    <input>problem</input>
    <output>candidate_solution_1</output>
  </node>
  <node id="2">
    <operator>agent_2</operator>
    <input>problem</input>
    <output>candidate_solution_2</output>
  </node>
  <node id="3">
    <operator>agent_3</operator>
    <input>problem</input>
    <output>candidate_solution_3</output>
  </node>
  <node id="4">
    <operator>ensemble</operator>
    <input>candidate_solution_1, candidate_solution_2, candidate_solution_3</input>
    <output>final_answer</output>
  </node>
  <edge from="1" to="4"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>