# Workflow ID: hotpotqa_579_0
# Benchmark: hotpotqa
# Data Indices: [1600, 304, 1280, 2583, 2598]

<operator id="0" type="agent">
    <instruction>Identify the parent company of the entity mentioned in the question.</instruction>
    <input>problem</input>
    <output>company_name</output>
  </operator>
  <operator id="1" type="agent">
    <instruction>Determine the location of the headquarters of the identified company.</instruction>
    <input>company_name</input>
    <output>headquarters_location</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Find the current head of the company headquartered in the specified location.</instruction>
    <input>headquarters_location</input>
    <output>company_head</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Verify that the company head is indeed the leader of the company based in Atlanta, GA, as per the context.</instruction>
    <input>company_head</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>