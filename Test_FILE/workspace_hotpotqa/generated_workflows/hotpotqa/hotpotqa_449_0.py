# Workflow ID: hotpotqa_449_0
# Benchmark: hotpotqa
# Data Indices: [2597, 1150, 2673, 1160]

<agent id="1">
    <instruction>Identify the key entities mentioned in the problem and their relationships.</instruction>
    <input>problem</input>
    <output>entity_list</output>
  </agent>
  <agent id="2">
    <instruction>Extract all potential candidates for the answer based on the context provided.</instruction>
    <input>entity_list</input>
    <output>candidates</output>
  </agent>
  <agent id="3">
    <instruction>Filter candidates using logical deduction from the problem's question and context clues.</instruction>
    <input>candidates</input>
    <output>filtered_candidates</output>
  </agent>
  <agent id="4">
    <instruction>Validate each filtered candidate against the full context to ensure accuracy.</instruction>
    <input>filtered_candidates</input>
    <output>validated_candidates</output>
  </agent>
  <agent id="5">
    <instruction>Rank the validated candidates by relevance and confidence score.</instruction>
    <input>validated_candidates</input>
    <output>ranked_candidates</output>
  </agent>
  <agent id="6">
    <instruction>Return the top-ranked candidate as the final answer.</instruction>
    <input>ranked_candidates</input>
    <output>final_answer</output>
  </agent>