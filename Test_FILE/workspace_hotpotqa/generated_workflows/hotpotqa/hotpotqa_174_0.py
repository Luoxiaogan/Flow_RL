# Workflow ID: hotpotqa_174_0
# Benchmark: hotpotqa
# Data Indices: [1752, 2317, 69, 1561]

<operator id="0">
    <instruction>Identify the key entities in the problem and determine what needs to be compared or analyzed.</instruction>
    <input>problem</input>
    <output>entity_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Extract numerical data related to the number of species for each genus from the context.</instruction>
    <input>entity_analysis</input>
    <output>species_data</output>
  </operator>
  <operator id="2">
    <instruction>Compare the number of species between the two genera using the extracted data.</instruction>
    <input>species_data</input>
    <output>comparison_result</output>
  </operator>
  <operator id="3">
    <instruction>Verify that the comparison result aligns with the given context and resolve any ambiguity.</instruction>
    <input>comparison_result</input>
    <output>verified_result</output>
  </operator>
  <operator id="4">
    <instruction>Formulate a clear and concise final answer based on the verified result.</instruction>
    <input>verified_result</input>
    <output>final_answer</output>
  </operator>
  <edge source="0" target="1"/>
  <edge source="1" target="2"/>
  <edge source="2" target="3"/>
  <edge source="3" target="4"/>