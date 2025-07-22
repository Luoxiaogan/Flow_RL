# Workflow ID: hotpotqa_399_0
# Benchmark: hotpotqa
# Data Indices: [1934, 1114, 771, 1234]

<start>
    <operator name="analyze_question" input="question" output="parsed_question"/>
  </start>

  <operator name="extract_context_keywords" input="context" output="keywords"/>
  
  <operator name="match_keywords_to_entities" input="parsed_question, keywords" output="candidate_entities"/>
  
  <operator name="validate_entities_with_domain_knowledge" input="candidate_entities" output="valid_entities"/>
  
  <operator name="generate_answer" input="valid_entities" output="answer"/>
  
  <operator name="verify_answer_consistency" input="answer, question" output="final_answer"/>
  
  <end output="final_answer"/>