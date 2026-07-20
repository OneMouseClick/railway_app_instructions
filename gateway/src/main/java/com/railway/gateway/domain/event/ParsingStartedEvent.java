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
public class ParsingStartedEvent extends BaseEvent {

    public ParsingStartedEvent(UUID taskId) {
        super("PARSING_STARTED");
        this.taskId = taskId;
        this.correlationId = taskId;
    }
}