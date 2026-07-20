package com.railway.gateway.domain.service;

import com.railway.gateway.domain.event.BaseEvent;

public interface EventPublisher {

    void publish(BaseEvent event);

    /**
     * Публикация рабочего события в document.exchange с явным routing key
     * (ai.analyze / assemble.document).
     */
    void publishToDocumentExchange(BaseEvent event, String routingKey);
}