package com.railway.gateway.infrastructure.service;

import com.railway.gateway.domain.event.BaseEvent;
import com.railway.gateway.domain.service.EventPublisher;
import com.railway.gateway.infrastructure.properties.RabbitMqProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class RabbitEventPublisher implements EventPublisher {

    private final RabbitTemplate rabbitTemplate;
    private final RabbitMqProperties rabbitMqProperties;

    @Override
    public void publish(BaseEvent event) {
        send(determineExchange(event), determineRoutingKey(event), event);
    }

    @Override
    public void publishToDocumentExchange(BaseEvent event, String routingKey) {
        send(rabbitMqProperties.getExchange().getDocument(), routingKey, event);
    }

    private void send(String exchange, String routingKey, BaseEvent event) {
        if (event.getEventId() == null) {
            event.setEventId(UUID.randomUUID());
        }

        log.debug("Publishing event: type={}, eventId={}, taskId={}, exchange={}, routingKey={}",
                event.getEventType(),
                event.getEventId(),
                event.getTaskId(),
                exchange,
                routingKey);

        rabbitTemplate.convertAndSend(exchange, routingKey, event, message -> {
            message.getMessageProperties().setCorrelationId(
                    event.getCorrelationId() != null ? event.getCorrelationId().toString() : null
            );
            message.getMessageProperties().setMessageId(event.getEventId().toString());
            return message;
        });
    }

    private String determineExchange(BaseEvent event) {
        return switch (event.getEventType()) {
            case "DOCUMENT_UPLOADED", "TASK_CREATED" -> rabbitMqProperties.getExchange().getDocument();
            case "PARSING_STARTED", "PARSED", "GENERATING_STARTED",
                 "GENERATED", "ASSEMBLING_STARTED", "COMPLETED", "FAILED",
                 "TASK_STATUS_CHANGED" -> rabbitMqProperties.getExchange().getTask();
            default -> rabbitMqProperties.getExchange().getTask();
        };
    }

    private String determineRoutingKey(BaseEvent event) {
        return switch (event.getEventType()) {
            case "DOCUMENT_UPLOADED", "TASK_CREATED" -> rabbitMqProperties.getRoutingKey().getDocumentParse();
            case "PARSING_STARTED", "PARSED", "GENERATING_STARTED",
                 "GENERATED", "ASSEMBLING_STARTED", "COMPLETED", "FAILED",
                 "TASK_STATUS_CHANGED" -> rabbitMqProperties.getRoutingKey().getTaskStatus();
            default -> rabbitMqProperties.getRoutingKey().getTaskStatus();
        };
    }
}