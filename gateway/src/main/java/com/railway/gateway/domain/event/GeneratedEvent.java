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
public class GeneratedEvent extends BaseEvent {

    private String generatedInstructionObjectKey;

    public GeneratedEvent(UUID taskId, String generatedInstructionObjectKey) {
        super("GENERATED");
        this.taskId = taskId;
        this.correlationId = taskId;
        this.generatedInstructionObjectKey = generatedInstructionObjectKey;
    }
}