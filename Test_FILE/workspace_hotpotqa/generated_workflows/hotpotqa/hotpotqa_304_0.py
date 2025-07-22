# Workflow ID: hotpotqa_304_0
# Benchmark: hotpotqa
# Data Indices: [1557, 564, 1917, 2851, 1296]

<agent id="1">
    <instruction>Extract key entities and relationships from the context relevant to the question.</instruction>
    <input>problem</input>
    <output>entities_and_relations</output>
  </agent>
  <agent id="2">
    <instruction>Identify the specific location mentioned in the context that matches the question's focus.</instruction>
    <input>entities_and_relations</input>
    <output>location_match</output>
  </agent>
  <agent id="3">
    <instruction>Determine which outlaw is directly associated with the identified location.</instruction>
    <input>location_match</input>
    <output>outlaw_association</output>
  </agent>
  <agent id="4">
    <instruction>Verify the connection between the outlaw and the house by cross-referencing historical details in the context.</instruction>
    <input>outlaw_association</input>
    <output>verification_result</output>
  </agent>
  <agent id="5">
    <instruction>Return the final answer based on verified association.</instruction>
    <input>verification_result</input>
    <output>final_answer</output>
  </agent>
  <connection>
    <from>1</from>
    <to>2</to>
  </connection>
  <connection>
    <from>2</from>
    <to>3</to>
  </connection>
  <connection>
    <from>3</from>
    <to>4</to>
  </connection>
  <connection>
    <from>4</from>
    <to>5</to>
  </connection>