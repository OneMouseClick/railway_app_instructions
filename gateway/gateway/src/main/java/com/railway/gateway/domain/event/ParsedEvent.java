package com.railway.gateway.domain.event;

import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.UUID;

@Data
@SuperBuilder
@NoArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class ParsedEvent extends BaseEvent {

    private String parsedContentObjectKey;

    public ParsedEvent(UUID taskId, String parsedContentObjectKey) {
        super("PARSED");
        this.taskId = taskId;
        this.correlationId = taskId;
        this.parsedContentObjectKey = parsedContentObjectKey;
    }
}