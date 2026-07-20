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
public class AssemblingStartedEvent extends BaseEvent {

    public AssemblingStartedEvent(UUID taskId) {
        super("ASSEMBLING_STARTED");
        this.taskId = taskId;
        this.correlationId = taskId;
    }
}