# Workflow ID: hotpotqa_580_0
# Benchmark: hotpotqa
# Data Indices: [1955, 3604, 2797, 3017]

<start/>
  <agent id="1" type="reasoning">
    <instruction>Identify the key entities and relationships in the problem. Break down the question to determine what information is needed to solve it.</instruction>
  </agent>
  <agent id="2" type="retrieval">
    <instruction>Extract relevant facts from the context that directly address the question. Focus on specific names, dates, or events mentioned.</instruction>
  </agent>
  <agent id="3" type="comparison">
    <instruction>Compare the extracted facts to determine the correct answer. If multiple candidates exist, use chronological or categorical logic to resolve ambiguity.</instruction>
  </agent>
  <agent id="4" type="verification">
    <instruction>Validate the answer against the context to ensure accuracy. Confirm no contradictions or missing details exist.</instruction>
  </agent>
  <end/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="end"/>