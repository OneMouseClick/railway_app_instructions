package com.railway.gateway.domain.service;

import com.railway.gateway.domain.event.BaseEvent;

public interface EventPublisher {

    void publish(BaseEvent event);
}