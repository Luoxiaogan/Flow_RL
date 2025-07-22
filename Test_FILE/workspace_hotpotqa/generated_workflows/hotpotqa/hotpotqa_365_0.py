# Workflow ID: hotpotqa_365_0
# Benchmark: hotpotqa
# Data Indices: [2502, 3956, 84, 736]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem statement. Focus on the main subject, associated roles, and relevant context.</instruction>
        <input>problem</input>
        <output>entity_map</output>
    </operator>
    <operator id="1">
        <instruction>Extract the specific question from the problem and determine what information is required to answer it directly.</instruction>
        <input>entity_map</input>
        <output>question_focus</output>
    </operator>
    <operator id="2">
        <instruction>Map the extracted question to relevant contextual data points. Ensure all links between entities are preserved for traceability.</instruction>
        <input>question_focus</input>
        <output>contextual_links</output>
    </operator>
    <operator id="3">
        <instruction>Verify that the contextual links contain sufficient evidence to resolve the question. If not, identify missing connections or refine the query.</instruction>
        <input>contextual_links</input>
        <output>validated_evidence</output>
    </operator>
    <operator id="4">
        <instruction>Generate a concise, accurate answer based on the validated evidence. Avoid overgeneralization or unsupported inference.</instruction>
        <input>validated_evidence</input>
        <output>final_answer</output>
    </operator>
    <operator id="5">
        <instruction>Double-check that the final answer aligns with the original question and that no irrelevant details were included.</instruction>
        <input>final_answer</input>
        <output>quality_check</output>
    </operator>
    <operator id="6">
        <instruction>Return the final validated answer as the output of this workflow.</instruction>
        <input>quality_check</input>
        <output>result</output>
    </operator>