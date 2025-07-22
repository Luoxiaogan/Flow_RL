# Workflow ID: hotpotqa_509_0
# Benchmark: hotpotqa
# Data Indices: [1508, 3808, 1229, 1423, 2847]

<operator id="0" type="agent">
    <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
  </operator>
  <operator id="1" type="agent">
    <instruction>Extract relevant details from the context that directly relate to the question being asked.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>Validate the extracted information against known facts or logical consistency to ensure accuracy.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Combine validated information to construct a precise and complete answer.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Verify the final output by cross-referencing with all provided context elements to avoid missing critical clues.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Ensure no extraneous or irrelevant data is included in the final response.</instruction>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>