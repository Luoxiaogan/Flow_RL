# Workflow ID: hotpotqa_339_0
# Benchmark: hotpotqa
# Data Indices: [2103, 2131, 3560, 1425, 1265]

<node id="1" type="input">
    <prompt>Understand the core question and identify key entities mentioned.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on one entity at a time to avoid redundancy.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information directly answers the question or requires further processing.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Apply logical reasoning or cross-reference with other extracted facts to resolve ambiguity or missing links.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Ensure all intermediate steps are aligned with the final goal: producing a concise, accurate answer.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the final answer based on the validated chain of reasoning.</prompt>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>