# Workflow ID: hotpotqa_268_0
# Benchmark: hotpotqa
# Data Indices: [3185, 3902, 252, 314]

<operator id="0" type="agent">
        <instruction>Identify the key entities and relationships in the problem. Break down the question into its core components to determine what information is needed to solve it.</instruction>
        <input>problem</input>
        <output>structured_query</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>Based on the structured query, retrieve relevant context from the provided knowledge base that directly addresses the question.</instruction>
        <input>structured_query</input>
        <output>relevant_context</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Extract the specific answer from the relevant context by focusing only on the entity or fact required to answer the question.</instruction>
        <input>relevant_context</input>
        <output>answer</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify the extracted answer against the original question to ensure accuracy and completeness. If the answer is ambiguous or incomplete, refine the search or re-evaluate the context.</instruction>
        <input>answer</input>
        <output>final_answer</output>
    </operator>
    <operator id="4" type="agent">
        <instruction>Validate the final answer using an independent reasoning path—cross-check with alternative pieces of evidence or logic derived from the same context.</instruction>
        <input>final_answer</input>
        <output>validated_answer</output>
    </operator>
    <operator id="5" type="agent">
        <instruction>Ensure the validated answer matches exactly what was asked in the question, without adding unnecessary details or omitting critical elements.</instruction>
        <input>validated_answer</input>
        <output>clean_final_output</output>
    </operator>