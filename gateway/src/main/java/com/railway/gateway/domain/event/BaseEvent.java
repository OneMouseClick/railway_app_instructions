package com.railway.gateway.domain.event;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.time.Instant;
import java.util.UUID;

@Data
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.EXISTING_PROPERTY, property = "eventType", visible = true)
@JsonSubTypes({
        @JsonSubTypes.Type(value = DocumentUploadedEvent.class, name = "DOCUMENT_UPLOADED"),
        @JsonSubTypes.Type(value = TaskCreatedEvent.class, name = "TASK_CREATED"),
        @JsonSubTypes.Type(value = ParsingStartedEvent.class, name = "PARSING_STARTED"),
        @JsonSubTypes.Type(value = ParsedEvent.class, name = "PARSED"),
        @JsonSubTypes.Type(value = GeneratingStartedEvent.class, name = "GENERATING_STARTED"),
        @JsonSubTypes.Type(value = GeneratedEvent.class, name = "GENERATED"),
        @JsonSubTypes.Type(value = AssemblingStartedEvent.class, name = "ASSEMBLING_STARTED"),
        @JsonSubTypes.Type(value = CompletedEvent.class, name = "COMPLETED"),
        @JsonSubTypes.Type(value = FailedEvent.class, name = "FAILED")
})
public abstract class BaseEvent {

    private UUID eventId;
    private String eventType;
    protected UUID correlationId;
    protected UUID taskId;
    private Instant timestamp;

    protected BaseEvent(String eventType) {
        this.eventId = UUID.randomUUID();
        this.eventType = eventType;
        this.timestamp = Instant.now();
    }
}