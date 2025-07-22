# Workflow ID: hotpotqa_59_0
# Benchmark: hotpotqa
# Data Indices: [3201, 1812, 2746, 1036, 2779]

<start/>
  <agent id="1" type="reasoning">
    <instruction>Identify the key elements in the question and determine which entity is being asked about.</instruction>
    <input>question</input>
    <output>entity_to_compare</output>
  </agent>
  <agent id="2" type="lookup">
    <instruction>Find the country of origin for each director mentioned in the context.</instruction>
    <input>context</input>
    <output>director_origin</output>
  </agent>
  <agent id="3" type="comparison">
    <instruction>Compare the origins of the two directors to determine which one is from the United States.</instruction>
    <input>entity_to_compare, director_origin</input>
    <output>us_director</output>
  </agent>
  <agent id="4" type="validation">
    <instruction>Verify that the identified director matches the criteria of being from the United States based on the context provided.</instruction>
    <input>us_director, context</input>
    <output>final_answer</output>
  </agent>
  <end/>