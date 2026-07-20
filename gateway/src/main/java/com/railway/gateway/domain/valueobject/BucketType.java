package com.railway.gateway.domain.valueobject;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum BucketType {

    SOURCE_DOCUMENTS("source-documents"),
    PARSED_JSON("parsed-json"),
    GENERATED_JSON("generated-json"),
    RESULT_DOCUMENTS("result-documents");

    private final String bucketName;
}