# Workflow ID: hotpotqa_450_0
# Benchmark: hotpotqa
# Data Indices: [3068, 1782, 437, 2011]

<start>
    <task>Extract relevant information from context</task>
    <agent>Extractor</agent>
  </start>

  <Extractor>
    <task>Identify key entities and relationships</task>
    <agent>Analyzer</agent>
  </Extractor>

  <Analyzer>
    <task>Map entities to answer the question</task>
    <agent>Mapper</agent>
  </Analyzer>

  <Mapper>
    <task>Validate against all context clues</task>
    <agent>Validator</agent>
  </Mapper>

  <Validator>
    <task>Ensure consistency with given constraints</task>
    <agent>Checker</agent>
  </Validator>

  <Checker>
    <task>Generate final answer</task>
    <agent>Answerer</agent>
  </Checker>

  <Answerer>
    <task>Output structured response</task>
    <output>Final Answer</output>
  </Answerer>