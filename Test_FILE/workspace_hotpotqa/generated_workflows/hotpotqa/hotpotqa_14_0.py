# Workflow ID: hotpotqa_14_0
# Benchmark: hotpotqa
# Data Indices: [1297, 1794, 629, 1836]

<operator id="1">
        <instruction>Identify the key entities and their relationships in the problem context. Focus on extracting structured information that directly answers the question.</instruction>
        <input>problem</input>
        <output>structured_entities</output>
    </operator>

    <operator id="2">
        <instruction>Verify if the extracted entities contain sufficient data to answer the question. If not, determine what additional information is needed from the context.</instruction>
        <input>structured_entities</input>
        <output>information_gap</output>
    </operator>

    <operator id="3">
        <instruction>Based on the information gap, locate relevant supporting details in the context that can resolve the ambiguity or missing data.</instruction>
        <input>information_gap</input>
        <output>supporting_details</output>
    </operator>

    <operator id="4">
        <instruction>Combine the supporting details with the original structured entities to form a complete and accurate answer.</instruction>
        <input>supporting_details</input>
        <output>final_answer</output>
    </operator>

    <operator id="5">
        <instruction>Validate the final answer by cross-checking it against the original problem statement and all provided context to ensure consistency and correctness.</instruction>
        <input>final_answer</input>
        <output>validated_answer</output>
    </operator>

    <operator id="6">
        <instruction>Ensure the output format matches the expected structure for this type of problem (e.g., list, string, number). If multiple answers exist, select the most precise one.</instruction>
        <input>validated_answer</input>
        <output>optimized_output</output>
    </operator>