package com.railway.gateway.infrastructure.properties;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@Data
@Validated
@ConfigurationProperties(prefix = "rabbitmq")
public class RabbitMqProperties {

    @NotBlank
    private String host;

    @NotNull
    private Integer port;

    @NotBlank
    private String username;

    @NotBlank
    private String password;

    @NotBlank
    private String virtualHost;

    private Listener listener = new Listener();
    private Exchange exchange = new Exchange();
    private Queue queue = new Queue();
    private RoutingKey routingKey = new RoutingKey();
    private DeadLetter deadLetter = new DeadLetter();
    private Retry retry = new Retry();

    @Data
    public static class Listener {
        private int concurrency = 1;
        private int maxConcurrency = 3;
        private int prefetch = 10;
    }

    @Data
    public static class Exchange {
        @NotBlank
        private String document;
        @NotBlank
        private String task;
        @NotBlank
        private String deadLetter;
    }

    @Data
    public static class Queue {
        @NotBlank
        private String documentParse;
        @NotBlank
        private String aiAnalyze;
        @NotBlank
        private String assembleDocument;
        @NotBlank
        private String taskStatus;
        @NotBlank
        private String deadLetter;
        @NotBlank
        private String retry;
    }

    @Data
    public static class RoutingKey {
        @NotBlank
        private String documentParse;
        @NotBlank
        private String aiAnalyze;
        @NotBlank
        private String assembleDocument;
        @NotBlank
        private String taskStatus;
        @NotBlank
        private String deadLetter;
        @NotBlank
        private String retry;
    }

    @Data
    public static class DeadLetter {
        private int ttl = 60000;
    }

    @Data
    public static class Retry {
        private int maxAttempts = 3;
        private int initialInterval = 1000;
        private double multiplier = 2.0;
    }
}