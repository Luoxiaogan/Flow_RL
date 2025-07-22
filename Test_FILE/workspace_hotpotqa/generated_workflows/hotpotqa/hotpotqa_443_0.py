# Workflow ID: hotpotqa_443_0
# Benchmark: hotpotqa
# Data Indices: [2798, 1732, 3233, 3711]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on birth dates and notable actions like adoption of orphans.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Identify the entertainer, activist, and French Resistance agent who adopted twelve orphans of different skin colors.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Confirm the birth date of the identified individual from the extracted data.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Validate that this person matches all criteria: entertainer, activist, French Resistance agent, and adopter of 12 diverse orphans.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the confirmed birth date as the final answer.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>