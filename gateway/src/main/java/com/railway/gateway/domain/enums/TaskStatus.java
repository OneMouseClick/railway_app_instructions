package com.railway.gateway.domain.enums;

public enum TaskStatus {
    CREATED,
    PARSING,
    PARSED,
    GENERATING,
    GENERATED,
    ASSEMBLING,
    COMPLETED,
    FAILED
}