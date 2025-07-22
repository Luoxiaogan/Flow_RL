# Workflow ID: hotpotqa_482_0
# Benchmark: hotpotqa
# Data Indices: [870, 1132, 2588, 2638]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the core question and relevant context.</instruction>
        <input>problem</input>
        <output>question_analysis</output>
    </agent>
    <agent id="2" type="retrieval">
        <instruction>Extract key entities and relationships from the context that relate to the question.</instruction>
        <input>question_analysis</input>
        <output>key_entities</output>
    </agent>
    <agent id="3" type="comparison">
        <instruction>Compare the roles or purposes of the two entities mentioned in the question using the extracted context.</instruction>
        <input>key_entities</input>
        <output>comparison_result</output>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify if the comparison aligns with explicit statements in the context. If not, re-evaluate based on strongest evidence.</instruction>
        <input>comparison_result</input>
        <output>verified_answer</output>
    </agent>
    <agent id="5" type="synthesis">
        <instruction>Formulate a clear, concise answer based on the verified result.</instruction>
        <input>verified_answer</input>
        <output>final_answer</output>
    </agent>