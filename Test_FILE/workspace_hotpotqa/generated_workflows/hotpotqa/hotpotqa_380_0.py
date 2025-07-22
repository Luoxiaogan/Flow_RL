# Workflow ID: hotpotqa_380_0
# Benchmark: hotpotqa
# Data Indices: [2632, 107, 3676, 98]

<operator id="0" type="agent">
        <instruction>
            Analyze the input context to identify key entities and relationships relevant to the question. Focus on extracting structured information that can be used to answer the query.
        </instruction>
    </operator>
    <operator id="1" type="agent">
        <instruction>
            From the extracted entities, determine which one directly answers the specific question. If multiple candidates exist, apply logical reasoning to select the best match based on contextual clues.
        </instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>
            Verify the selected candidate by cross-referencing with other parts of the context to ensure accuracy and avoid false positives or misinterpretations.
        </instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>
            If verification confirms correctness, return the answer. Otherwise, re-evaluate the reasoning path and refine the selection using alternative evidence from the context.
        </instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>
            Finalize the output by ensuring it aligns with the question's intent and is expressed clearly and concisely without any ambiguity.
        </instruction>
    </operator>
    <operator id="5" type="agent">
        <instruction>
            Optionally, generate a confidence score for the answer based on the strength of supporting evidence in the context.
        </instruction>
    </operator>
    <operator id="6" type="agent">
        <instruction>
            Combine all outputs from previous steps into a coherent final response, including the answer and optional confidence score if available.
        </instruction>
    </operator>