# Workflow ID: hotpotqa_142_0
# Benchmark: hotpotqa
# Data Indices: [1777, 57, 2881, 546]

<start>
        <operator name="identify_key_question" prompt="What is the core question asking? Break it down step by step." />
        <operator name="extract_relevant_context" prompt="From the context, what information directly answers the question? List only key facts." />
        <operator name="validate_and_filter" prompt="Is the extracted information sufficient and accurate to answer the question? Remove irrelevant details." />
    </start>

    <operator name="synthesize_answer" prompt="Based on the filtered information, construct a concise and precise answer. Think step by step." />

    <end>
        <output name="final_answer" />
    </end>

    <edge from="identify_key_question" to="extract_relevant_context" />
    <edge from="extract_relevant_context" to="validate_and_filter" />
    <edge from="validate_and_filter" to="synthesize_answer" />
    <edge from="synthesize_answer" to="end" />