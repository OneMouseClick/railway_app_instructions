package com.railway.gateway.domain.service;

import com.railway.gateway.domain.event.BaseEvent;

public interface EventListener {

    void handle(BaseEvent event);
}