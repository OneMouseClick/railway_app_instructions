package com.railway.gateway.infrastructure.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.flywaydb.core.Flyway;
import org.springframework.boot.autoconfigure.flyway.FlywayMigrationStrategy;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Slf4j
@Configuration
@RequiredArgsConstructor
public class FlywayConfig {

    @Bean
    public FlywayMigrationStrategy flywayMigrationStrategy() {
        return (Flyway flyway) -> {
            log.info("Starting Flyway migration...");
            log.info("Current schema version before migration: {}", flyway.info().current() != null ?
                    flyway.info().current().getVersion() : "none");
            flyway.migrate();
            log.info("Flyway migration completed successfully.");
            log.info("Current schema version after migration: {}", flyway.info().current().getVersion());
        };
    }
}