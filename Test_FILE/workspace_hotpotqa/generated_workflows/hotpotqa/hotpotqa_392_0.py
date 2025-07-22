# Workflow ID: hotpotqa_392_0
# Benchmark: hotpotqa
# Data Indices: [3428, 183, 2070, 2238, 2590]

<operator id="1" type="agent">
        <instruction>Think step by step to identify the key entities and relationships in the problem. Focus on extracting the core question and relevant context.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Based on the extracted information, determine the specific entity that answers the question. Ensure no irrelevant details are included in your response.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify that the answer aligns with the context provided and check for any contradictions or ambiguities in the reasoning path.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Refine the final answer to ensure clarity and precision. Avoid including extra explanations unless explicitly required.</instruction>
    </operator>
    <operator id="5" type="agent">
        <instruction>Check if all previous operators have contributed meaningfully to the output. If not, reprocess the critical steps to ensure completeness.</instruction>
    </operator>
    <operator id="6" type="agent">
        <instruction>Generate a concise, correct, and well-structured answer based on the verified result from the previous steps.</instruction>
    </operator>
    <operator id="7" type="agent">
        <instruction>Ensure the final output is free of any problem-specific references and only contains the solution as per the optimized workflow.</instruction>
    </operator>
    <operator id="8" type="agent">
        <instruction>Validate the graph structure: confirm it has between 3 and 8 nodes, uses only allowed operators, and avoids redundancy or missing logic flow.</instruction>
    </operator>