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
public class GeneratingStartedEvent extends BaseEvent {

    public GeneratingStartedEvent(UUID taskId) {
        super("GENERATING_STARTED");
        this.taskId = taskId;
        this.correlationId = taskId;
    }
}