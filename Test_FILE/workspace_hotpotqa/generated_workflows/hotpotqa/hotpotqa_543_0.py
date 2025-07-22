# Workflow ID: hotpotqa_543_0
# Benchmark: hotpotqa
# Data Indices: [3706, 2113, 964, 1091, 1462]

<operator id="0" type="reasoning">
    <instruction>Identify the key elements in the question: the American actress born in 1996, her role in Tragedy Girls, and the character she portrayed in Deadpool.</instruction>
    <input>problem</input>
    <output>actor_info</output>
  </operator>
  <operator id="1" type="search">
    <instruction>Find the American actress born in 1996 who starred in Tragedy Girls. Cross-reference with known cast lists to confirm.</instruction>
    <input>problem</input>
    <output>confirmed_actor</output>
  </operator>
  <operator id="2" type="lookup">
    <instruction>Look up the character played by the confirmed actress in the film Deadpool.</instruction>
    <input>confirmed_actor</input>
    <output>character_in_deadpool</output>
  </operator>
  <operator id="3" type="validate">
    <instruction>Verify that the character from Deadpool matches the information in the context provided about the actress's roles.</instruction>
    <input>character_in_deadpool</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>