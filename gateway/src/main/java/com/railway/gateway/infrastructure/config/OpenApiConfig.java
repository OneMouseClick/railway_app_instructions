package com.railway.gateway.infrastructure.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI railwayGatewayOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Railway AI Platform - Gateway API")
                        .description("Gateway service API for Railway AI Platform. " +
                                "Manages document uploads, task lifecycle, and result retrieval. " +
                                "Use the /api/v1/auth/login or /api/v1/auth/register endpoints to obtain a JWT token.")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Railway AI Platform Team")
                                .email("contact@railway-ai-platform.com"))
                        .license(new License()
                                .name("Proprietary")
                                .url("https://railway-ai-platform.com/license")))
                .addSecurityItem(new SecurityRequirement().addList("Bearer Authentication"))
                .components(new Components()
                        .addSecuritySchemes("Bearer Authentication",
                                new SecurityScheme()
                                        .name("Bearer Authentication")
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                                        .description("Enter JWT Bearer token obtained from /api/v1/auth/login")));
    }
}