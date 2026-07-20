package com.railway.gateway.infrastructure.service;

import com.railway.gateway.application.service.TaskService;
import com.railway.gateway.domain.event.AssemblingStartedEvent;
import com.railway.gateway.domain.event.BaseEvent;
import com.railway.gateway.domain.event.CompletedEvent;
import com.railway.gateway.domain.event.FailedEvent;
import com.railway.gateway.domain.event.GeneratedEvent;
import com.railway.gateway.domain.event.GeneratingStartedEvent;
import com.railway.gateway.domain.event.ParsedEvent;
import com.railway.gateway.domain.event.ParsingStartedEvent;
import com.railway.gateway.domain.service.EventListener;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class RabbitEventListener implements EventListener {

    private final TaskService taskService;

    @Override
    @RabbitListener(
            queues = "${rabbitmq.queue.task-status}",
            concurrency = "${rabbitmq.listener.concurrency}",
            containerFactory = "rabbitListenerContainerFactory"
    )
    public void handle(BaseEvent event) {
        log.info("Received event: type={}, eventId={}, taskId={}, correlationId={}",
                event.getEventType(),
                event.getEventId(),
                event.getTaskId(),
                event.getCorrelationId());

        switch (event) {
            case ParsingStartedEvent e ->
                    taskService.updateStatusToParsing(e.getTaskId());
            case ParsedEvent e ->
                    taskService.markParsed(e.getTaskId(), e.getParsedContentObjectKey());
            case GeneratingStartedEvent e ->
                    taskService.updateStatusToGenerating(e.getTaskId());
            case GeneratedEvent e ->
                    taskService.markGenerated(e.getTaskId(), e.getGeneratedInstructionObjectKey());
            case AssemblingStartedEvent e ->
                    taskService.updateStatusToAssembling(e.getTaskId());
            case CompletedEvent e ->
                    taskService.markCompleted(e.getTaskId(), e.getResultMinioObjectName());
            case FailedEvent e ->
                    taskService.markFailed(e.getTaskId(), e.getErrorMessage());
            default ->
                    log.warn("Unhandled event type: {}", event.getEventType());
        }
    }
}