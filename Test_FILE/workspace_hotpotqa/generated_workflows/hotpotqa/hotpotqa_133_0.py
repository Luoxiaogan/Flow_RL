# Workflow ID: hotpotqa_133_0
# Benchmark: hotpotqa
# Data Indices: [2325, 3625, 295, 1096]

<start>
    <operator id="agent1" type="question_analysis">
      <instruction>Break down the question to identify key entities and relationships. Focus on the main subject, the attribute being asked, and any contextual clues.</instruction>
    </operator>
  </start>

  <agent1>
    <operator id="agent2" type="context_retrieval">
      <instruction>From the provided context, locate information directly related to the key entities identified in the question. Extract only relevant sentences or phrases that answer the core query.</instruction>
    </operator>
  </agent1>

  <agent2>
    <operator id="agent3" type="reasoning">
      <instruction>Use logical deduction based on the extracted context. If multiple candidates exist, compare their relevance to the question. Eliminate irrelevant options and focus on the best match.</instruction>
    </operator>
  </agent2>

  <agent3>
    <operator id="agent4" type="verification">
      <instruction>Double-check your reasoning against the original context. Ensure no misinterpretation occurred and confirm that the selected answer is explicitly supported by the text.</instruction>
    </operator>
  </agent3>

  <agent4>
    <operator id="agent5" type="output_generation">
      <instruction>Generate the final answer as a concise, clear statement that directly addresses the question. Avoid adding extra details not requested.</instruction>
    </operator>
  </agent4>

  <agent5>
    <end/>
  </agent5>