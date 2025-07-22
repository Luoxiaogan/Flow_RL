# Workflow ID: hotpotqa_61_0
# Benchmark: hotpotqa
# Data Indices: [3849, 2151, 2846, 3247]

<operator id="1" type="reasoning">
        <instruction>Identify the key elements in the question and determine what information is needed to answer it.</instruction>
        <input>problem</input>
        <output>query_analysis</output>
    </operator>

    <operator id="2" type="retrieval">
        <instruction>Extract relevant details from the context that match the query analysis.</instruction>
        <input>query_analysis, context</input>
        <output>relevant_info</output>
    </operator>

    <operator id="3" type="comparison">
        <instruction>Compare the extracted information to identify the correct answer based on the comparison criteria.</instruction>
        <input>relevant_info</input>
        <output>candidate_answer</output>
    </operator>

    <operator id="4" type="verification">
        <instruction>Verify the candidate answer against the context to ensure accuracy and consistency.</instruction>
        <input>candidate_answer, context</input>
        <output>final_answer</output>
    </operator>

    <operator id="5" type="ensemble">
        <instruction>Combine outputs from multiple operators to enhance confidence in the final result.</instruction>
        <input>final_answer, candidate_answer</input>
        <output>optimized_result</output>
    </operator>

    <operator id="6" type="validation">
        <instruction>Validate that the optimized result meets all constraints: correctness, clarity, and completeness.</instruction>
        <input>optimized_result</input>
        <output>validated_output</output>
    </operator>

    <operator id="7" type="formatting">
        <instruction>Format the validated output into a clean, structured response suitable for the user.</instruction>
        <input>validated_output</input>
        <output>final_response</output>
    </operator>