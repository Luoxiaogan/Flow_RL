# Workflow ID: hotpotqa_560_0
# Benchmark: hotpotqa
# Data Indices: [3771, 714, 940, 3571]

<agent id="1" type="question_analysis">
    <instruction>Break down the question into key components and identify the core subject to search for.</instruction>
  </agent>
  <agent id="2" type="context_search">
    <instruction>Scan the provided context for any mention of the key components identified in the question.</instruction>
  </agent>
  <agent id="3" type="entity_extraction">
    <instruction>Extract relevant entities (names, roles, events) that match the question's focus from the context.</instruction>
  </agent>
  <agent id="4" type="verification">
    <instruction>Verify that the extracted entity directly answers the question based on contextual evidence.</instruction>
  </agent>
  <agent id="5" type="output_generation">
    <instruction>Generate a concise, accurate final answer using only verified information.</instruction>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>