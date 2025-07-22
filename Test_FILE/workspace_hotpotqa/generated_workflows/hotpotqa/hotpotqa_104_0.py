# Workflow ID: hotpotqa_104_0
# Benchmark: hotpotqa
# Data Indices: [2376, 2300, 534, 1696, 2817]

<operator id="1">
        <instruction>Identify the key entities and their relationships in the problem statement. Break down the question into its core components.</instruction>
        <input>problem</input>
        <output>structured_analysis</output>
    </operator>
    
    <operator id="2">
        <instruction>Extract relevant context information that directly addresses the question. Filter out unrelated details to focus on evidence.</instruction>
        <input>structured_analysis, context</input>
        <output>filtered_context</output>
    </operator>
    
    <operator id="3">
        <instruction>Compare the extracted information to determine which entity satisfies the condition in the question.</instruction>
        <input>filtered_context</input>
        <output>comparison_result</output>
    </operator>
    
    <operator id="4">
        <instruction>Verify the conclusion by cross-referencing with known facts or additional context if available.</instruction>
        <input>comparison_result, filtered_context</input>
        <output>verification_result</output>
    </operator>
    
    <operator id="5">
        <instruction>Formulate a concise answer based on the verified result, ensuring it directly answers the original question.</instruction>
        <input>verification_result</input>
        <output>final_answer</output>
    </operator>
    
    <operator id="6">
        <instruction>Review the entire reasoning chain for logical consistency and completeness.</instruction>
        <input>final_answer, verification_result</input>
        <output>reviewed_output</output>
    </operator>
    
    <operator id="7">
        <instruction>Output the final validated answer as per the problem's requirements.</instruction>
        <input>reviewed_output</input>
        <output>answer</output>
    </operator>