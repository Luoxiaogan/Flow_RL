# Workflow ID: hotpotqa_317_0
# Benchmark: hotpotqa
# Data Indices: [2910, 1206, 3974, 3558]

<start>
        <operator name="extract_question" input="problem" output="question"/>
        <operator name="extract_context" input="problem" output="context"/>
    </start>

    <operator name="identify_key_entities" input="context" output="entities"/>
    <operator name="parse_question_intent" input="question" output="intent"/>

    <operator name="match_entities_to_intent" input="entities, intent" output="candidates"/>
    
    <operator name="validate_candidates" input="candidates" output="valid_answers"/>
    
    <operator name="generate_answer" input="valid_answers" output="final_answer"/>
    
    <end>
        <output name="final_answer" />
    </end>