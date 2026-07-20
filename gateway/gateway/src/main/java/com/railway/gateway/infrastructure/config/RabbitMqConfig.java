package com.railway.gateway.infrastructure.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.railway.gateway.infrastructure.properties.RabbitMqProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.config.RetryInterceptorBuilder;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.rabbit.retry.RejectAndDontRequeueRecoverer;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.retry.interceptor.RetryOperationsInterceptor;

@Slf4j
@Configuration
@RequiredArgsConstructor
public class RabbitMqConfig {

    private final RabbitMqProperties rabbitMqProperties;

    /* ========== Exchanges ========== */

    @Bean
    public TopicExchange documentExchange() {
        return new TopicExchange(rabbitMqProperties.getExchange().getDocument());
    }

    @Bean
    public TopicExchange taskExchange() {
        return new TopicExchange(rabbitMqProperties.getExchange().getTask());
    }

    @Bean
    public TopicExchange deadLetterExchange() {
        return new TopicExchange(rabbitMqProperties.getExchange().getDeadLetter());
    }

    /* ========== Queues ========== */

    @Bean
    public Queue documentParseQueue() {
        return QueueBuilder.durable(rabbitMqProperties.getQueue().getDocumentParse())
                .deadLetterExchange(rabbitMqProperties.getExchange().getDeadLetter())
                .deadLetterRoutingKey(rabbitMqProperties.getRoutingKey().getDeadLetter())
                .build();
    }

    @Bean
    public Queue aiAnalyzeQueue() {
        return QueueBuilder.durable(rabbitMqProperties.getQueue().getAiAnalyze())
                .deadLetterExchange(rabbitMqProperties.getExchange().getDeadLetter())
                .deadLetterRoutingKey(rabbitMqProperties.getRoutingKey().getDeadLetter())
                .build();
    }

    @Bean
    public Queue assembleDocumentQueue() {
        return QueueBuilder.durable(rabbitMqProperties.getQueue().getAssembleDocument())
                .deadLetterExchange(rabbitMqProperties.getExchange().getDeadLetter())
                .deadLetterRoutingKey(rabbitMqProperties.getRoutingKey().getDeadLetter())
                .build();
    }

    @Bean
    public Queue taskStatusQueue() {
        return QueueBuilder.durable(rabbitMqProperties.getQueue().getTaskStatus())
                .deadLetterExchange(rabbitMqProperties.getExchange().getDeadLetter())
                .deadLetterRoutingKey(rabbitMqProperties.getRoutingKey().getDeadLetter())
                .build();
    }

    @Bean
    public Queue deadLetterQueue() {
        return QueueBuilder.durable(rabbitMqProperties.getQueue().getDeadLetter()).build();
    }

    @Bean
    public Queue retryQueue() {
        return QueueBuilder.durable(rabbitMqProperties.getQueue().getRetry())
                .ttl(rabbitMqProperties.getDeadLetter().getTtl())
                .deadLetterExchange(rabbitMqProperties.getExchange().getDocument())
                .deadLetterRoutingKey(rabbitMqProperties.getRoutingKey().getRetry())
                .build();
    }

    /* ========== Bindings ========== */

    @Bean
    public Binding documentParseBinding() {
        return BindingBuilder.bind(documentParseQueue())
                .to(documentExchange())
                .with(rabbitMqProperties.getRoutingKey().getDocumentParse());
    }

    @Bean
    public Binding aiAnalyzeBinding() {
        return BindingBuilder.bind(aiAnalyzeQueue())
                .to(documentExchange())
                .with(rabbitMqProperties.getRoutingKey().getAiAnalyze());
    }

    @Bean
    public Binding assembleDocumentBinding() {
        return BindingBuilder.bind(assembleDocumentQueue())
                .to(documentExchange())
                .with(rabbitMqProperties.getRoutingKey().getAssembleDocument());
    }

    @Bean
    public Binding taskStatusBinding() {
        return BindingBuilder.bind(taskStatusQueue())
                .to(taskExchange())
                .with(rabbitMqProperties.getRoutingKey().getTaskStatus());
    }

    @Bean
    public Binding deadLetterBinding() {
        return BindingBuilder.bind(deadLetterQueue())
                .to(deadLetterExchange())
                .with(rabbitMqProperties.getRoutingKey().getDeadLetter());
    }

    @Bean
    public Binding retryBinding() {
        return BindingBuilder.bind(retryQueue())
                .to(deadLetterExchange())
                .with(rabbitMqProperties.getRoutingKey().getRetry());
    }

    /* ========== Message Converter ========== */

    @Bean
    public MessageConverter messageConverter() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return new Jackson2JsonMessageConverter(objectMapper);
    }

    /* ========== RabbitTemplate ========== */

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(messageConverter());
        rabbitTemplate.setMandatory(true);

        rabbitTemplate.setConfirmCallback((correlationData, ack, cause) -> {
            if (correlationData != null) {
                if (ack) {
                    log.debug("Message confirmed: {}", correlationData.getId());
                } else {
                    log.error("Message not confirmed: {}, cause: {}", correlationData.getId(), cause);
                }
            }
        });

        rabbitTemplate.setReturnsCallback(returned -> {
            log.error("Message returned: exchange={}, routingKey={}, replyCode={}, replyText={}",
                    returned.getExchange(),
                    returned.getRoutingKey(),
                    returned.getReplyCode(),
                    returned.getReplyText());
        });

        return rabbitTemplate;
    }

    /* ========== Retry Interceptor ========== */

    @Bean
    public RetryOperationsInterceptor retryInterceptor() {
        return RetryInterceptorBuilder.stateless()
                .maxAttempts(rabbitMqProperties.getRetry().getMaxAttempts())
                .backOffOptions(
                        rabbitMqProperties.getRetry().getInitialInterval(),
                        rabbitMqProperties.getRetry().getMultiplier(),
                        rabbitMqProperties.getDeadLetter().getTtl())
                .recoverer(new RejectAndDontRequeueRecoverer())
                .build();
    }
}